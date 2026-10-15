from repositories.system.Texts import TextsRepository


class TextsService:
    def __init__(self, repo: TextsRepository):
        self.repo = repo

    def create_text(self, the_text: str):
        return self.repo.create({"the_text": the_text})

    def get_text(self, text_id: int):
        return self.repo.get_by_id(text_id)

    def get_all_texts(self):
        return self.repo.get_all()

    def update_text(self, text_id: int, new_text: str):
        return self.repo.update(text_id, {"the_text": new_text})

    def delete_text(self, text_id: int):
        return self.repo.delete_by_id(text_id)