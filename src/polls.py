from functions import create_table
from json import dumps

conn, cur = create_table()
class Poll:
    def __init__(self, variants: list, multiple: bool, title: str):
        self.title: str = title
        self.variants: dict = self.process_variants(variants)
        self.multiple: bool = multiple
    def process_variants(self, variants):
        return {variant: [] for variant in variants}
        
    def show_results(self):
        return self.results
    
    def create_poll(self):
        cur.execute('''
            INSERT INTO polls (title, variants, multiple)
            VALUES (%s, %s, %s)
        ''', (self.title, dumps(self.variants), self.multiple))
        conn.commit()