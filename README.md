# Distribuição Equiparada via Método de Hamilton

Este é um aplicativo **Streamlit** simples para **distribuir membros de equipe** entre diferentes seções, com base na contagem de itens em cada seção. O projeto utiliza o **Método do Maior Resto** (também conhecido como **Método de Hamilton**) para garantir uma alocação justa e proporcional, mesmo com um número pequeno de membros.

Você pode encontrar o programa em: [https://distribution-algorithm.streamlit.app/](https://distribution-algorithm.streamlit.app/)

## 🛠️ Como Funciona?

O aplicativo oferece uma interface interativa onde você pode:

1.  **Inserir os nomes** de todos os membros da equipe.
2.  **Definir a contagem** de itens para até quatro seções.

Ao clicar no botão "Executar Distribuição", o aplicativo:

1.  **Calcula as porcentagens-alvo** para cada seção, aplicando um limiar mínimo dinâmico para evitar que qualquer seção ativa receba uma porcentagem muito baixa.
2.  **Embaralha aleatoriamente** a lista de membros para garantir uma distribuição imprevisível e imparcial.
3.  **Aplica o Método do Maior Resto** para distribuir os membros com base nas porcentagens calculadas. Este método garante que os membros restantes após a divisão proporcional sejam alocados nas seções com os maiores "restos", resultando em uma distribuição mais equilibrada.
4.  **Exibe o resultado**, mostrando quais membros foram alocados em cada seção.
