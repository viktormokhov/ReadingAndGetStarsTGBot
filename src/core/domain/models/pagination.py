from dataclasses import dataclass

@dataclass
class PageParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return self.page * self.page_size
