"""
Lyricizer : Guesses the artist from your song lyrics !
"""

import argparse
import dill
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from gooey import Gooey
from gooey import GooeyParser


@Gooey(default_size=(800, 600))
def parse_args():
    parser = GooeyParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Thanks for using Lyricizer!",
    )
    parser.add_argument(
        "-l",
        "--lyrics",
        help="Lyrics of the song to be predicted",
        type=str,
        metavar="",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Path to the pickled models. Defaults to the last trained model.",
        type=str,
        default="models__Blink182_FooFighters_GreenDay_SB19_Smile_Sum41_TheOffspring_Yellowcard.pkl",
        metavar="",
        widget="FileChooser",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=int,
        choices=[0, 1, 2, 3, 4, 5, 6, 7],
        help="Choice of estimator, defaults to best.\n 0 = Random Forest\n 1 = XGBoost\n 2 = GradientBoosting\n 3 = Logistic Regression\n 4 = Naive Bayes\n 5 = SVC\n 6 = RidgeClassifier\n 7 = KNeighbors",
        default=5,
        metavar="",
    )

    # Implement all arguments
    args = parser.parse_args()

    return args


def main(args):
    print("\n", "-------------------------", "\n")

    # Load model, pick it
    print("Loading model from ", args.path)
    with open(args.path, "rb") as file:
        models = dill.load(file)
    chosen_model = models[args.model]
    print("With this model, we can only identify the following bands:")
    print(models[0].y_test.unique())
    # Since we have used CountVectorizer and TfidfTransformer in the original model we can just pass the lyrics as a list
    # If TfidfVectorizer was used, we need to transform the lyrics first before passing it as a list.
    tf_lyrics = [args.lyrics]
    # Predict class probability
    print("This model estimates that your song belongs to this band:")
    try:
        for idx, pipe_class in enumerate(chosen_model.pipe.classes_):
            print(
                round(100 * (chosen_model.pipe.predict_proba(tf_lyrics)[0][idx]), 2),
                "% chance that the lyrics you entered belong to band:",
                pipe_class,
            )
    except:
        print(chosen_model.pipe.predict(tf_lyrics))

if __name__ == "__main__":
    main(parse_args())
