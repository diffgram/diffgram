from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from walrus.methods.task.task_template import task_template_launch_handler
from walrus.methods.text_data.text_tokenizer import TextTokenizer
from unittest.mock import patch
from nltk.tokenize import word_tokenize, sent_tokenize


class TestTextTokenizer(testing_setup.DiffgramBaseTestCase):
    """



    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestTextTokenizer, self).setUp()
        self.project_data = data_mocking.create_project_with_context(
            {
                'users': [
                    {'username': 'Test',
                     'email': 'test@test.com',
                     'password': 'diffgram123',
                     }
                ]
            },
            self.session
        )
        self.project = self.project_data['project']
        self.text = 'this is a sentence. Hello world.'

    def test___tokenize_word_nltk(self):
        tokenizer = TextTokenizer(type = 'nltk')
        with patch('walrus.methods.text_data.text_tokenizer.word_tokenize') as mock1:
            result = tokenizer._TextTokenizer__tokenize_word_nltk(self.text)
            mock1.assert_called_once()

    def test__tokenize_sentence_nltk(self):
        tokenizer = TextTokenizer(type = 'nltk')
        with patch('walrus.methods.text_data.text_tokenizer.sent_tokenize') as mock1:
            result = tokenizer._TextTokenizer__tokenize_sentence_nltk(self.text)
            mock1.assert_called_once()

    def test_get_word_tokenizer_function(self):
        tokenizer = TextTokenizer(type = 'nltk')
        result = tokenizer.get_word_tokenizer_function()
        self.assertEqual(result, tokenizer._TextTokenizer__tokenize_word_nltk)

    def test_get_sentence_tokenizer_function(self):
        tokenizer = TextTokenizer(type = 'nltk')
        result = tokenizer.get_sentence_tokenizer_function()
        self.assertEqual(result, tokenizer._TextTokenizer__tokenize_sentence_nltk)

    def test_tokenize_words(self):
        # Test NLTK type
        tokenizer = TextTokenizer(type = 'nltk')
        result = tokenizer.tokenize_words(self.text)
        self.assertEqual(result,
                         [{'value': 'this', 'tag': ''},
                          {'value': 'is', 'tag': ''},
                          {'value': 'a', 'tag': ''},
                          {'value': 'sentence', 'tag': ''},
                          {'value': '.', 'tag': ''},
                          {'value': 'Hello', 'tag': ''},
                          {'value': 'world', 'tag': ''},
                          {'value': '.', 'tag': ''},
                          {'value': '\n', 'tag': ''},
                          ]
                         )

    def test_tokenize_sentences(self):
        # Test NLTK type
        tokenizer = TextTokenizer(type = 'nltk')
        result = tokenizer.tokenize_sentences(self.text)
        self.assertEqual(result, [{'value': 'this is a sentence.', 'tag': ''}, {'value': 'Hello world.', 'tag': ''}])
