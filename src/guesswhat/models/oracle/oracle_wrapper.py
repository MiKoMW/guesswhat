
from generic.tf_utils.evaluator import Evaluator


class OracleWrapper(object):
    def __init__(self, oracle, tokenizer):

        self.oracle = oracle
        self.evaluator = None
        self.tokenizer = tokenizer

    def initialize(self, sess):
        self.evaluator = Evaluator(self.oracle.get_sources(sess), self.oracle.scope_name)

    def answer_question(self, sess, question, seq_length, game_data):

        game_data["is_training"] = False

        game_data["question"] = question
        game_data["seq_length"] = seq_length

        # convert dico name to fit oracle constraint
        game_data["category"] = game_data.get("targets_category", None)
        game_data["spatial"] = game_data.get("targets_spatial", None)

        game_data["image"] = game_data.get("image", None)
        game_data["image_mask"] = game_data.get("image_mask", None)

        game_data["crop"] = game_data.get("crop", None)
        game_data["crop_mask"] = game_data.get("crop_mask", None)

        # get answer
        answers_indices = self.evaluator.execute(sess, output=self.oracle.best_pred, batch=game_data)
        answers = [self.tokenizer.oracle_idx_to_answers[a] for a in answers_indices]

        return answers


class OracleUserWrapper(object):
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def initialize(self, sess):
        pass

    def answer_question(self, sess, question, **_):

        # Discard question if it contains the stop dialogue token
        if self.tokenizer.stop_dialogue in question[0]:
            return [self.tokenizer.non_applicable_token]

        print()
        print("Q :", self.tokenizer.decode(question[0]))

        while True:
            answer = input('A (Yes,No,N/A): ').lower()
            if answer == "y" or answer == "yes":
                token = self.tokenizer.yes_token
                break

            elif answer == "n" or answer == "no":
                token = self.tokenizer.no_token
                break

            elif answer == "na" or answer == "n/a" or answer == "not applicable":
                token = self.tokenizer.non_applicable_token
                break

            else:
                print("Invalid answer...")

        return [token]