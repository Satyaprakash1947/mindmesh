from dataclasses import dataclass, field

from app.ai.service import TutorService
from app.graph.repository import GraphRepository
from app.settings import Settings


@dataclass
class Runtime:
    settings: Settings
    graph: GraphRepository
    tutor: TutorService
    sessions: dict[str, str] = field(default_factory=dict)

    def close(self) -> None:
        self.graph.close()
