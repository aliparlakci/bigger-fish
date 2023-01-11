import argparse
import pandas
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import top_k_accuracy_score
from sklearn.model_selection import train_test_split, ShuffleSplit, cross_val_score

class Warehouse:
    def __init__(self):
        self.trace_len = -1 
        self.data_points =  pandas.DataFrame()

    def insert(self, row):
        self._validate_trace(row[0])

        trace = row[0]
        codec, browser, player, platform, user, timestamp = row[1:]
        new_data_point = pandas.DataFrame(data=[[*trace, codec, browser, player, platform, user, timestamp]], columns=[*range(1,len(trace)+1), "codec", "browser", "player", "platform", "user", "timestamp"])
        data_points = pandas.concat((data_points, new_data_point))

    def get_df(self):
        return self.data_points

    def _validate_trace(self, trace):
        if self.trace_len == -1:
            self.trace_len = len(trace)
        else:
            if self.trace_len != len(trace):
                raise Exception()

class Evaluator:
    def __init__(self, warehouse):
        self.warehouse: Warehouse = warehouse

    def _filter_data_points(self, browser, player, codec, platform, user) -> pandas.DataFrame:
        df = self.warehouse.data_points

        if browser != "*":
            df = df[df["browser"] == browser]
        
        if codec != "*":
            df = df[df["codec"] == codec]
        
        if player != "*":
            df = df[df["player"] == player]

        if platform != "*":
            df = df[df["platform"] == platform]

        if user != "*":
            df = df[df["user"] == user]
        
        return df

    def _preprocess(self, df, target):
        le = LabelEncoder()
        for column in ["browser", "player", "codec", "platform", "user"]:
            df[column] = le.fit_transform(df[column])
        
        y = df[target]
        X = df.drop(columns=[target, "timestamp"])

        return X, y

    def _generate_model(self, X, y, test_size=0.2):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, stratify=y)
        
        clf = RandomForestClassifier()
        clf = clf.fit(X_train, y_train)

        y_probs = clf.predict_proba(X_test)
        top1 = top_k_accuracy_score(y_test, y_probs, k=1)

        return top1

    def evaluate(self, target, relaxations):
        labels = self.warehouse.get_column(target)

        browser_choices = "*" if "browser" in relaxations else self.data_points["browser"].unique()
        player_choices = "*" if "player" in relaxations else self.data_points["player"].unique()
        codec_choices = "*" if "codec" in relaxations else self.data_points["codec"].unique()
        platform_choices = "*" if "platform" in relaxations else self.data_points["platform"].unique()
        user_choices = "*" if "user" in relaxations else self.data_points["user"].unique()

        combinations = np.meshgrid(browser_choices, player_choices, codec_choices, platform_choices, user_choices)
        combinations = np.array(combinations).T.reshape(-1, 5)

        for browser, player, codec, platform, user in combinations:
            df = self._filter_data_points(browser, player, codec, platform, user)
            X, y = self._preprocess(df, target)
            
            shuffle_split = ShuffleSplit(n_splits=10, test_size=0.2)
            clf = RandomForestClassifier()
            scores = cross_val_score(clf, X, y, cv=shuffle_split, scoring="accuracy")
            
            print(f"{browser}, {player}, {codec}, {platform}, {user} -> {len(df)} data points: {np.mean(scores):.2f}% (+/- {np.std(scores):.2f})")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["codec", "player", "browser", "platform", "user"])
    parser.add_argument("--relax", choices=["codec", "player", "browser", "platform", "user"], nargs="*", default=[])
    opts = parser.parse_args()
    
if __name__ == "__main__":
    main()