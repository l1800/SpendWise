from models.core.CategoryStandard import CategoryStandard


class CategoryStandardRepository:

    def __init__(self, session):
        self.session = session

    def get_all(self):
        return self.session.query(CategoryStandard).all()

    def get_by_id(self, benchmark_id):
        return self.session.query(CategoryStandard).filter_by(
            benchmark_id=benchmark_id
        ).first()

    def get_by_category(self, category_id):
        return self.session.query(CategoryStandard).filter_by(
            category_id=category_id
        ).first()

    def create(self, obj):
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj):
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj):
        self.session.delete(obj)
        self.session.commit()

    def get_by_category_id(self, category_id):
        return (
            self.session.query(CategoryStandard)
            .filter_by(category_id=category_id)
            .first()
        )
    def get_category_standards(self):
        return (
            self.session.query(CategoryStandard)
            .filter(CategoryStandard.is_active == True)
            .all()
        )