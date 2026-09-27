class ErroDeNegocio(Exception):
    def __init__(self, mensagem: str, codigo: str):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.codigo = codigo
        # O graphql-core copia este atributo para o campo "extensions" da resposta.
        self.extensions = {"code": codigo}
