import os
import sys
from unittest.mock import MagicMock, patch

# -------------------------------------------------------
# Add prediction folder to Python path
# -------------------------------------------------------

CURRENT_DIR = os.path.dirname(__file__)
PREDICTION_DIR = os.path.abspath(
    os.path.join(CURRENT_DIR, "..", "prediction")
)

sys.path.insert(0, PREDICTION_DIR)

import load_model


# -------------------------------------------------------
# Test: Successful Loading
# -------------------------------------------------------

def test_load_artifacts_success():

    fake_model = MagicMock(name="TensorFlowModel")
    fake_preprocessor = MagicMock(name="Preprocessor")

    load_model._model = None
    load_model._preprocessor = None

    with patch("load_model.tf.keras.models.load_model",
               return_value=fake_model) as mock_tf:

        with patch("load_model.joblib.load",
                   return_value=fake_preprocessor) as mock_joblib:

            model, preprocessor = load_model.load_artifacts()

            assert model == fake_model
            assert preprocessor == fake_preprocessor

            mock_tf.assert_called_once()
            mock_joblib.assert_called_once()


# -------------------------------------------------------
# Test: Model is Cached
# -------------------------------------------------------

def test_model_cached():

    fake_model = MagicMock()
    fake_preprocessor = MagicMock()

    load_model._model = fake_model
    load_model._preprocessor = fake_preprocessor

    model, preprocessor = load_model.load_artifacts()

    assert model == fake_model
    assert preprocessor == fake_preprocessor


# -------------------------------------------------------
# Test: TensorFlow Loading Failure
# -------------------------------------------------------

def test_model_load_failure():

    load_model._model = None
    load_model._preprocessor = None

    with patch(
        "load_model.tf.keras.models.load_model",
        side_effect=Exception("Model not found")
    ):

        try:
            load_model.load_artifacts()
            assert False

        except Exception as e:
            assert str(e) == "Model not found"


# -------------------------------------------------------
# Test: Preprocessor Loading Failure
# -------------------------------------------------------

def test_preprocessor_load_failure():

    fake_model = MagicMock()

    load_model._model = None
    load_model._preprocessor = None

    with patch(
        "load_model.tf.keras.models.load_model",
        return_value=fake_model
    ):

        with patch(
            "load_model.joblib.load",
            side_effect=Exception("Preprocessor missing")
        ):

            try:
                load_model.load_artifacts()
                assert False

            except Exception as e:
                assert str(e) == "Preprocessor missing"