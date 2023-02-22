import time
import subprocess
from platform import platform
from selenium.webdriver import Safari
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium import webdriver


def get_process_parent_id_of(process_name):
    p = subprocess.run(f"pidof {process_name}" + " | awk {'print $NF'}", capture_output=True, shell=True)
    process_parent_id = p.stdout.decode()
    return int(process_parent_id.strip())

class TraceCollector:
    def __init__(self, url="http://localhost:7777", trace_length=10, headless=False, sandbox=True):
        self.url = url
        self.trace_length = trace_length
        self.cores = -1
        self.browser = "CHROME"

    def setCores(self, core_number):
        self.cores = core_number

    def setChrome(self, headless=False, sandbox=True):
        self.browser = "CHROME"
        options = webdriver.chrome.options.Options()
        if headless:
            options.add_argument("--headless")
        if not sandbox:
            options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=options)

    def setFirefox(self, headless=False, sandbox=True):
        self.browser = "FIREFOX"
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        if not sandbox:
            options.add_argument("--no-sandbox")
        self.driver = webdriver.Firefox(options=options)

    def setEdge(self, headless=False, sandbox=True):
        self.browser = "EDGE"
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless")
        if not sandbox:
            options.add_argument("--no-sandbox")
        self.driver = webdriver.Edge(options=options)

    def setSafari(self, headless=False, sandbox=True):
        self.browser = "SAFARI"
        self.driver = webdriver.Safari()
        if headless:
            # Not possible to run Safari in headless mode
            print("Running Safari in non-headless mode because headless mode is not supported.")

    def collect_traces(self):
        self.__run()
        self.driver.execute_script('window.collectTrace("ours")')
        time.sleep(self.trace_length)
        return self.__get_traces()

    def __get_traces(self) -> list:
        while True:
            traces = self.driver.execute_script("return traces;")
            if len(traces):
                return traces[0]

    def __run(self):
        self.driver.switch_to.window(self.driver.current_window_handle)
        self.driver.get(self.url)
        
        if self.cores != -1 and "linux" in platform.lower():
            if self.browser == "FIREFOX":
                ppid = get_process_parent_id_of("firefox")
            elif self.browser == "CHROME":
                ppid = get_process_parent_id_of("chrome")

            taskset_process = subprocess.run(f"taskset -p {self.cores} {ppid}")
            taskset_process.check_returncode()

            irqbalance_process = subprocess.run(f"irqbalance --banirq=0")
            irqbalance_process.check_returncode()

        self.driver.execute_script(f"window.trace_length = {self.trace_length * 1000}")
        self.driver.execute_script("window.using_automation_script = true")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()


if __name__ == "__main__":
    with TraceCollector(trace_length=10) as collector:
        traces = collector.collect_traces()
        print(traces)
