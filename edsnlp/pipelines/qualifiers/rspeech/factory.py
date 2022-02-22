from typing import List, Optional

from spacy.language import Language

from edsnlp.pipelines.qualifiers.rspeech import ReportedSpeech
from edsnlp.utils.deprecation import deprecated_factory

DEFAULT_CONFIG = dict(
    pseudo=None,
    preceding=None,
    following=None,
    quotation=None,
    verbs=None,
    attr="NORM",
    on_ents_only=True,
    within_ents=False,
    explain=False,
)


@deprecated_factory("rspeech", "eds.rspeech", default_config=DEFAULT_CONFIG)
@Language.factory("eds.rspeech", default_config=DEFAULT_CONFIG)
def create_component(
    nlp: Language,
    name: str,
    attr: str,
    pseudo: Optional[List[str]],
    preceding: Optional[List[str]],
    following: Optional[List[str]],
    quotation: Optional[List[str]],
    verbs: Optional[List[str]],
    on_ents_only: bool,
    within_ents: bool,
    explain: bool,
):
    return ReportedSpeech(
        nlp=nlp,
        attr=attr,
        pseudo=pseudo,
        preceding=preceding,
        following=following,
        quotation=quotation,
        verbs=verbs,
        on_ents_only=on_ents_only,
        within_ents=within_ents,
        explain=explain,
    )
