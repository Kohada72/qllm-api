from pydantic import BaseModel, Field, ConfigDict



class TrainConfig(BaseModel):
    model_name: str = Field("facebook/opt-125m", description="使用するモデル名")
    data_seed: int = Field(42, ge=0, description="データサンプリングのシード値")
    dataset: str = Field("wikitext", description="データセットを指定")
    n_train: int = Field(4000, ge=1, description="学習データサンプル数")
    n_valid: int = Field(500, ge=1, description="バリデーションデータサンプル数")
    n_test: int = Field(500, ge=1, description="テストデータサンプル数")
    epochs: int = Field(10, ge=1, description="エポック数")
    lr: float = Field(2e-4, gt=0, description="学習率")


class ModelConfig(BaseModel):
    params_seed: int = Field(42, ge=0, description="モデルパラメータ初期化時のシード値")
    token_length: int = Field(512, ge=1, description="予測トークン最大長")
    bond_dim: int = Field(4, ge=1, le=10, description="MPOのbond次元")
    n_qubits: int = Field(4, ge=1, le=10, description="量子ビット数(無効化時: 中間次元)")
    use_qnn: bool = Field(True, description="QNN有効化設定")
    n_layers: int = Field(1, ge=1, le=10, description="回路の深さ(レイヤー数)")


class PredictionRequest(BaseModel):
    exp_title: str = Field("Test experiment", description="実験タイトルの設定")

    train_params: TrainConfig = Field(default_factory=TrainConfig)
    model_params: ModelConfig = Field(default_factory=ModelConfig)

    model_config = ConfigDict(from_attributes=True)