import os

class TemplateParser:
    def __init__(self, language: str = None, default_language="en"):
            self.current_path = os.path.dirname(os.path.abspath(__file__))
            self.default_language = default_language
            
            self.language = None
            self.set_language(language)
            
            
    def set_language(self, language: str):
        if not language:
            return None
        else:
            self.language = self.default_language
        
        language_path = os.path.join(self.current_path, "locales", language)
        if os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language
            
    def get(self, group: str, key: str, vars: dict = {}):
        """
            targeted_language: folder name [en, ar]
            
            group: file name [rag]
            key: variable name inside the file [document prompt]
            vars: the key is a Template so it may need values to be retrieved correct
        """
        
        targeted_language = self.language
        
        if not group or not key:
            return None
        
        group_path = os.path.join(self.current_path, "locales", self.language, f"{group}.py")
        
        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, "locales", self.default_language, f"{group}.py")
            targeted_language = self.default_language
            
        if not os.path.exists(group_path):
            return None
        
        # import group module -> # duck typing - magic method
        module = __import__(f"stores.llm.templates.locales.{targeted_language}.{group}", fromlist=[group]) 
        
        if not module:
            return None
        
        # getattr helps me search for a specific variable in a module 
        key_attribute = getattr(module, key) # key: is the prompt [system, document, footer]
        
        # NOTE: the key is a Template var (which waiting for some variables to be passed to avoid error)
        return key_attribute.substitute(vars)
        