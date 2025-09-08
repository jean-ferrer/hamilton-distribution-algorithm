import streamlit as st
import numpy as np
import math


# --- Funções de Lógica ---

def calculate_target_percentages(item_counts):
    """
    Calcula as porcentagens alvo para cada seção, ignorando seções com 0 itens
    e aplicando um threshold mínimo dinâmico baseado no número de seções ativas.
    """
    # Filtra apenas as galerias com contagem > 0 e guarda seus índices originais
    active_indices = [i for i, count in enumerate(item_counts) if count > 0]
    active_counts = [item_counts[i] for i in active_indices]
    
    num_total_sections = len(item_counts)
    num_active_sections = len(active_counts)

    # Se nenhuma galeria tiver itens, retorna uma distribuição zerada.
    if num_active_sections == 0:
        return [0.0] * num_total_sections

    # Define os thresholds dinâmicos baseados no número de galerias ativas
    thresholds = {
        4: 0.22,  # 22% para 4 galerias
        3: 0.27,  # 27% para 3 galerias
        2: 0.40,  # 40% para 2 galerias
        1: 1.00   # 100% para 1 galeria
    }
    min_percentage_threshold = thresholds.get(num_active_sections, 0) # Padrão para 0 se não encontrar

    # O resto da lógica é aplicada apenas às galerias ativas
    total_items = sum(active_counts)
    if total_items <= 0:
        # Este caso é pouco provável devido ao filtro anterior, mas é uma segurança
        return [0.0] * num_total_sections

    initial_percentages = [count / total_items for count in active_counts]
    adjusted_percentages = list(initial_percentages)
    total_deficit = 0
    indices_below_threshold = []

    for i in range(num_active_sections):
        if adjusted_percentages[i] < min_percentage_threshold:
            deficit = min_percentage_threshold - adjusted_percentages[i]
            total_deficit += deficit
            adjusted_percentages[i] = min_percentage_threshold
            indices_below_threshold.append(i)

    if total_deficit > 0:
        total_surplus_mass = sum(max(0, initial_percentages[i] - min_percentage_threshold) for i in range(num_active_sections) if i not in indices_below_threshold)
        
        indices_above_threshold = [i for i in range(num_active_sections) if i not in indices_below_threshold]

        if total_surplus_mass > 1e-9:
            for i in indices_above_threshold:
                surplus = max(0, initial_percentages[i] - min_percentage_threshold)
                contribution_ratio = surplus / total_surplus_mass
                reduction = total_deficit * contribution_ratio
                adjusted_percentages[i] -= reduction
                adjusted_percentages[i] = max(min_percentage_threshold, adjusted_percentages[i])

    # Normaliza para garantir que a soma seja exatamente 1
    current_sum = sum(adjusted_percentages)
    if abs(current_sum - 1.0) > 1e-9 and current_sum > 0:
        adjusted_percentages = [p / current_sum for p in adjusted_percentages]

    # Remonta a lista de porcentagens na ordem original, preenchendo 0 para as inativas
    final_percentages = [0.0] * num_total_sections
    for i, original_index in enumerate(active_indices):
        final_percentages[original_index] = adjusted_percentages[i]

    return final_percentages

def distribute_team_members(team_members, target_percentages):
    """
    Distribui membros da equipe nas seções usando o Método do Maior Resto.
    """
    num_members = len(team_members)
    num_sections = len(target_percentages)

    if num_members == 0:
        return [[] for _ in range(num_sections)]

    quotas = [p * num_members for p in target_percentages]
    assigned_counts = [math.floor(q) for q in quotas]
    remainders = [quotas[i] - assigned_counts[i] for i in range(num_sections)]

    assigned_so_far = sum(assigned_counts)
    remaining_to_assign = num_members - assigned_so_far

    remainder_indices = sorted(range(num_sections), key=lambda i: remainders[i], reverse=True)

    for i in range(remaining_to_assign):
        section_index = remainder_indices[i]
        assigned_counts[section_index] += 1

    distributions = []
    current_index = 0
    for count in assigned_counts:
        distributions.append(list(team_members[current_index : current_index + count]))
        current_index += count

    return distributions


# --- Interface com Streamlit ---

st.set_page_config(page_title="Distribuição de Equipe", layout="centered")

# Colunas para organizar a entrada de dados, com uma coluna de espaçamento no meio
col1, col_spacer, col2 = st.columns([1, 0.2, 1])

with col1:
    st.subheader("Membros da Equipe")

    if 'num_member_inputs' not in st.session_state:
        st.session_state.num_member_inputs = 6 

    team_members = []
    
    num_cols_members = 2
    cols_members = st.columns(num_cols_members)
    
    for i in range(st.session_state.num_member_inputs):
        with cols_members[i % num_cols_members]:
            member_name = st.text_input(
                label=f"Caixa do Membro {i+1}",
                label_visibility="collapsed",
                placeholder="Nome...",
                key=f"member_{i}"
            )
            if member_name.strip():
                team_members.append(member_name.strip())

    if st.button("Adicionar Membro ➕"):
        st.session_state.num_member_inputs += 1
        st.rerun()

# Espaçamento visual
with col_spacer:
    st.write("") # Adiciona um elemento vazio para ocupar o espaço

with col2:
    st.subheader("Contagem de Galeria")
    item_counts = []
    
    num_cols_gallery = 2
    cols_gallery = st.columns(num_cols_gallery)

    for i in range(4):
        with cols_gallery[i % num_cols_gallery]:
            count = st.number_input(
                f"Galeria {i+1}",
                min_value=0,
                step=1,
                key=f"gallery_{i}"
            )
            item_counts.append(count)

st.markdown("---")

# Botão para executar a distribuição
if st.button("Executar Distribuição", use_container_width=True, type="primary"):
    if not team_members:
        st.error("Por favor, insira pelo menos um nome de membro da equipe.")
    else:
        num_members = len(team_members)
        shuffled_members = np.random.permutation(team_members)

        target_percentages = calculate_target_percentages(item_counts)
        distributions = distribute_team_members(shuffled_members, target_percentages)

        st.success("Distribuição realizada com sucesso!")

        num_cols = 2  
        cols = st.columns(num_cols)

        for i, members_in_section in enumerate(distributions):
            with cols[i % num_cols]:
                num_members_in_section = len(members_in_section)
                
                st.markdown(f"<h3 style='font-size: 28px;'>Galeria {i+1}</h3>", unsafe_allow_html=True)
                
                if members_in_section:
                    members_str = " – ".join([f"<span style='font-size: 22px;'>{name}</span>" for name in members_in_section])
                    st.markdown(members_str, unsafe_allow_html=True)
                else:
                    st.markdown("<p style='font-size: 22px; color: grey;'>NENHUM</p>", unsafe_allow_html=True)
                
                st.markdown("---")
