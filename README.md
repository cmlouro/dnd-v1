# Jogo de Aventura

Um jogo de aventura 2D desenvolvido em Python usando Pygame.

## Funcionalidades

### Sistema de Jogador
- Movimento com setas ou WASD
- Pulo com barra de espaço
- Barra de vida e mana
- Sistema de níveis e experiência
- Inventário de itens
- Habilidades mágicas

### Habilidades Mágicas
- **Bola de Fogo** (tecla Q)
  - Custa 10 de mana
  - Cooldown de 1 segundo
  - Causa dano aos NPCs
  - Explode ao atingir um NPC
  - Efeito visual de explosão com círculos concêntricos

- **Teleporte** (tecla E)
  - Custa 30 de mana
  - Cooldown de 10 segundos
  - Teleporta o jogador na direção que está olhando

### Sistema de Inventário
- Pressione I para abrir/fechar o inventário
- Colete poções de vida no mapa
- Use itens com as teclas 1-4 (correspondendo à posição no inventário)
- Interface visual com grade de itens
- Descrições dos itens no inventário

### Sistema de Objetivos
- Objetivos visíveis na tela
- Progresso mostrado em tempo real
- Mensagem de conclusão quando objetivo é atingido
- Objetivo atual: Eliminar 2 NPCs

### NPCs
- Movimento autônomo
- 2 pontos de vida
- Barra de vida visível
- Hitbox maior para facilitar acertos
- Efeito visual de dano (flash vermelho)
- Balão de fala quando jogador se aproxima
- Desaparecem quando derrotados

### Ambiente
- Mapa procedural com diferentes biomas
- Castelos que podem ser explorados
- Áreas de água com piranhas
- Sistema de câmera que segue o jogador
- Interface limpa e intuitiva

### Controles
- **Setas/WASD**: Movimento
- **Espaço**: Pular
- **Q**: Usar Bola de Fogo
- **E**: Usar Teleporte
- **I**: Abrir/Fechar Inventário
- **1-4**: Usar Item do Inventário
- **ESC**: Pausar Jogo

## Instalação

1. Certifique-se de ter Python 3.x instalado
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Execute o jogo:
   ```
   python main.py
   ```

## Estrutura do Projeto

```
.
├── main.py              # Arquivo principal do jogo
├── game/
│   ├── player.py        # Classe do jogador
│   ├── map.py          # Sistema de mapa
│   ├── items.py        # Sistema de itens e habilidades
│   ├── npc.py          # Sistema de NPCs
│   ├── piranha.py      # Sistema de piranhas
│   ├── game_state.py   # Gerenciamento de estados
│   └── objectives.py   # Sistema de objetivos
└── assets/
    └── images/         # Recursos gráficos
        ├── items/      # Imagens de itens
        └── ...         # Outras imagens
```

## Desenvolvimento

O jogo foi desenvolvido usando:
- Python 3.x
- Pygame 2.5.2
- Sistema de sprites e animações
- Sistema de colisão personalizado
- Geração procedural de mapas
- Sistema de estados para gerenciamento do jogo

## Contribuição

Sinta-se à vontade para contribuir com o projeto! Algumas ideias:
- Adicionar novos tipos de NPCs
- Criar novas habilidades mágicas
- Implementar mais objetivos
- Adicionar efeitos sonoros
- Melhorar a interface do usuário 