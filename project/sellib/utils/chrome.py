from abc import ABC, abstractmethod
from selenium import webdriver

class Chrome(ABC):
    def __init__(
        self,
        options=False,
        auto_open_devtools_for_tab=False
    ):
        self.options = options
        if options:
            if auto_open_devtools_for_tab:
                self.chrome_add_options()
                
    chrome_options = webdriver.ChromeOptions()
    
    @abstractmethod
    def run(self):
        raise NotImplementedError("Should be implemented in subclass")
    
    def chrome_add_options(self):
        self.chrome_options.add_argument("--auto-open-devtools-for-tabs")
    
    def set_up(self):
        if self.options:
            self.chrome_driver = webdriver.Chrome(options=self.chrome_options)
        else:
            self.chrome_driver = webdriver.Chrome()
    
    def __call__(self):
        return self.run()
    
    def teardown(self):
        self.chrome_driver.quit()