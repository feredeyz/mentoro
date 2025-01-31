class Poll:
    '''
        Класс для создания опросов.
        title (str) - заголовок опроса
        variants (list) - список вариантов для выбора
        multiple (bool) - можно ли выбирать несколько вариантов ответа
        voted (list) - список проголосовавших людей
        results (dict) - результаты опроса ({вариант1: список проголосовавших, вариант2: список проголосовавших})
    '''
    
    def __init__(self, variants: list, multiple: bool, title: str):
        self.title: str = title
        self.variants: list = variants
        self.multiple: bool = multiple
        self.voted: list = []
        self.results: dict = {variant: 0 for variant in variants}
        
    def show_results(self):
        return self.results
    
    def check_vote(self):
        pass
    
    def create_poll(self):
        pass
    