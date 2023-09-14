import spacy
from typing import Iterable, List, Optional
import builtins

from libcpp cimport bool as cbool

from spacy.attrs cimport IS_ALPHA, IS_ASCII, IS_DIGIT, IS_LOWER, IS_PUNCT, IS_SPACE
from spacy.lexeme cimport Lexeme
from spacy.tokens.token cimport TokenC

from .terms import punctuation

cdef class FastSentenceSegmenter(object):
    """
    Segments the Doc into sentences using a rule-based strategy,
    specific to AP-HP documents.

    Applies the same rule-based pipeline as spaCy's sentencizer,
    and adds a simple rule on the new lines : if a new line is followed by a
    capitalised word, then it is also an end of sentence.

    DOCS: https://spacy.io/api/sentencizer

    Arguments
    ---------
    punct_chars : Optional[List[str]]
        Punctuation characters.
    use_endlines : bool
        Whether to use endlines prediction.
    """

    def __init__(
          self,
          vocab,
          *,
          punct_chars,
          use_endlines = None,
          ignore_excluded = True,
    ):
        if punct_chars is None:
            punct_chars = punctuation

        if use_endlines is not None:
            print("The use_endlines parameter of eds.sentences is deprecated and has been replaced by the ignore_excluded parameter")

        self.ignore_excluded = builtins.bool(ignore_excluded or use_endlines)
        self.newline_hash = vocab.strings["\n"]
        self.excluded_hash = vocab.strings["EXCLUDED"]
        self.endline_hash = vocab.strings["ENDLINE"]
        self.punct_chars_hash = {vocab.strings[c] for c in punct_chars}
        self.capitalized_shapes_hash = {
            vocab.strings[shape]
            for shape in ("Xx", "Xxx", "Xxxx", "Xxxxx")
        }

    def __call__(self, doc: spacy.tokens.Doc):
        self.process(doc)
        return doc

    cdef void process(self, Doc doc) nogil:
        """
        Segments the document in sentences.

        Arguments
        ---------
        docs: Iterable[Doc]
            A list of spacy Doc objects.
        """
        cdef TokenC token
        cdef cbool seen_period
        cdef cbool seen_newline
        cdef cbool is_in_punct_chars
        cdef cbool is_newline

        seen_period = False
        seen_newline = False

        if doc.length == 0:
            return

        for i in range(doc.length):
            # To set the attributes at False by default for the other tokens
            doc.c[i].sent_start = 1 if i == 0 else -1

            token = doc.c[i]

            if self.ignore_excluded and token.tag == self.excluded_hash:
                continue

            is_in_punct_chars = (
                  self.punct_chars_hash.const_find(token.lex.orth)
                  != self.punct_chars_hash.const_end()
            )
            is_newline = (
                  Lexeme.c_check_flag(token.lex, IS_SPACE)
                  and token.lex.orth == self.newline_hash
            )

            if seen_period or seen_newline:
                if seen_period and Lexeme.c_check_flag(token.lex, IS_DIGIT):
                    continue
                if (
                      is_in_punct_chars
                      or is_newline
                      or Lexeme.c_check_flag(token.lex, IS_PUNCT)
                ):
                    continue
                if seen_period:
                    doc.c[i].sent_start = 1
                    seen_newline = False
                    seen_period = False
                else:
                    doc.c[i].sent_start = (
                        1 if (
                              self.capitalized_shapes_hash.const_find(token.lex.shape)
                              != self.capitalized_shapes_hash.const_end()
                        ) else -1
                    )
                    seen_newline = False
                    seen_period = False
            elif is_in_punct_chars:
                seen_period = True
            elif is_newline:
                seen_newline = True
