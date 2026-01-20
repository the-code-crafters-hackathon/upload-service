class CategoriaProduto():
    def __init__(self, nome: str):
        self.nome = nome

    model_config = {
        "from_attributes": True
    }