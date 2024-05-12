from spacy.tokens import Span

import edsnlp
import edsnlp.pipes as eds


def test_ner():
    nlp = edsnlp.blank("eds")
    nlp.add_pipe(
        eds.extractive_qa(
            embedding=eds.transformer(
                model="prajjwal1/bert-tiny",
                window=20,
                stride=10,
            ),
            # During training, where do we get the gold entities from ?
            target_span_getter=["ner-gold"],
            # Which prompts for each label ?
            questions={
                "PERSON": "Quels sont les personnages ?",
                "GIFT": "Quels sont les cadeaux ?",
            },
            questions_attribute="question",
            # During prediction, where do we set the predicted entities ?
            span_setter="ents",
        ),
    )

    doc = nlp(
        "L'aîné eut le Moulin, le second eut l'âne, et le plus jeune n'eut que le Chat."
    )
    doc._.question = {
        "FAVORITE": ["Qui a eu de l'argent ?"],
    }
    # doc[0:2], doc[4:5], doc[6:8], doc[9:11], doc[13:16], doc[20:21]
    doc.spans["ner-gold"] = [
        Span(doc, 0, 2, "PERSON"),  # L'aîné
        Span(doc, 4, 5, "GIFT"),  # Moulin
        Span(doc, 6, 8, "PERSON"),  # le second
        Span(doc, 9, 11, "GIFT"),  # l'âne
        Span(doc, 13, 16, "PERSON"),  # le plus jeune
        Span(doc, 20, 21, "GIFT"),  # Chat
    ]
    nlp.post_init([doc])

    ner = nlp.pipes.extractive_qa
    batch = ner.prepare_batch([doc], supervision=True)
    results = ner.module_forward(batch)

    pred = list(ner.pipe([doc]))[0]
    print(pred.ents)

    assert results["loss"] is not None
    trf_inputs = [
        seq.replace(" [PAD]", "")
        for seq in ner.embedding.tokenizer.batch_decode(batch["embedding"]["input_ids"])
    ]
    assert trf_inputs == [
        "[CLS] quels sont les cadeaux? [SEP] l'aine eut le moulin, le second eut l'ane, et [SEP]",  # noqa: E501
        "[CLS] quels sont les cadeaux? [SEP] le second eut l'ane, et le plus jeune n'eut que le [SEP]",  # noqa: E501
        "[CLS] quels sont les cadeaux? [SEP] le plus jeune n'eut que le chat. [SEP]",  # noqa: E501
        "[CLS] quels sont les personnages? [SEP] l'aine eut le moulin, le second eut l'ane, et [SEP]",  # noqa: E501
        "[CLS] quels sont les personnages? [SEP] le second eut l'ane, et le plus jeune n'eut que le [SEP]",  # noqa: E501
        "[CLS] quels sont les personnages? [SEP] le plus jeune n'eut que le chat. [SEP]",  # noqa: E501
        "[CLS] qui a eu de l'argent? [SEP] l'aine eut le moulin, le second eut l'ane, et [SEP]",  # noqa: E501
        "[CLS] qui a eu de l'argent? [SEP] le second eut l'ane, et le plus jeune n'eut que le [SEP]",  # noqa: E501
        "[CLS] qui a eu de l'argent? [SEP] le plus jeune n'eut que le chat. [SEP]",  # noqa: E501
    ]
    assert batch["targets"].squeeze(2).tolist() == [
        [0, 0, 0, 0, 4, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0],
        [2, 3, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 2, 1, 3, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
