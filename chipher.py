import streamlit as st
import math

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Криптошифр",  layout="centered")

# Кастомный CSS для красоты
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput, .stTextArea, .stNumberInput { border-radius: 10px !important; }
    .stButton>button { width: 100%; border-radius: 20px; background: linear-gradient(45deg, #00f2fe 0%, #4facfe 100%); color: white; border: none; }
    .result-box { padding: 20px; border-radius: 15px; background-color: #1e2130; border-left: 5px solid #4facfe; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

st.title("Сервис быстрого шифрования")
st.write("Используйте на свое усмотрение мы не несем отвественности ни за что")


# --- ЛОГИКА ШИФРОВ ---

def caesar_cipher(text, shift, mode='enc'):
    result = ""
    # Ограничиваемся диапазоном печатных символов (от пробела до конца кириллицы)
    # Или просто используем сдвиг по кодам, но с проверкой
    s = shift if mode == 'enc' else -shift
    for char in text:
        # Берем код символа и просто двигаем его
        # Чтобы не было проблем с невидимыми символами, используем более сейвовый диапазон
        new_code = ord(char) + s
        result += chr(new_code)
    return result

def xor_cipher(text, key):
    result = ""
    for i in range(len(text)):
        result += chr(ord(text[i]) ^ ord(key[i % len(key)]))
    return result


def iterative_egcd(a, b):
    x, y, u, v = 0, 1, 1, 0
    while a != 0:
        q, r = b // a, b % a
        m, n = x - u * q, y - v * q
        b, a, x, y, u, v = a, r, u, v, m, n
    return b, x, y

def modInverse(e, phi):
    g, x, y = iterative_egcd(e, phi)
    if g != 1:
        return None
    else:
        return x % phi
# --- ИНТЕРФЕЙС ---

tab1, tab2, tab3 = st.tabs(["Цезарь", "XOR Логика", "Baby-RSA"])

with tab1:
    st.subheader("Шифр Цезаря")

    # Добавляем выбор режима, чтобы не путаться
    c_mode = st.radio("Режим:", ["Зашифровать", "Расшифровать"], key="c_mode_choice")

    col1, col2 = st.columns([2, 1])
    with col1:
        msg = st.text_area("Текст:", placeholder="Введите текст сюда...", key="c_msg")
    with col2:
        shift = st.number_input("Сдвиг (ключ):", value=3, step=1, key="c_shift_val")

    if st.button("Выполнить преобразование"):
        if c_mode == "Зашифровать":
            res = caesar_cipher(msg, shift, 'enc')
            st.write("Результат (копируй это):")
            st.code(res)
        else:
            res = caesar_cipher(msg, shift, 'dec')
            st.write("Расшифрованный текст:")
            st.success(res)

with tab2:
    st.subheader("XOR Шифрование (Биты)")
    msg_xor = st.text_input("Текст для XOR:", key="x_msg")
    key_xor = st.text_input("Ключ (слово):", value="KEY", key="x_key")

    if st.button("Выполнить XOR преобразование"):
        res = xor_cipher(msg_xor, key_xor)
        st.markdown("**Результат (в символах):**")
        st.code(res)
        st.markdown("**Результат (в битах):**")
        st.write(" ".join(format(ord(c), '08b') for c in res))

with tab3:
    st.subheader("Конструктор RSA")
    st.write("Выберите два простых числа (например, 61 и 53 или 17 и 19)")

    col_p, col_q, col_e = st.columns(3)
    with col_p:
        p = st.number_input("Число p:", value=61)
    with col_q:
        q = st.number_input("Число q:", value=53)
    with col_e:
        e = st.number_input("Экспонента e:", value=17)

    # Математические вычисления на лету
    n = p * q
    phi = (p - 1) * (q - 1)
    d = modInverse(e, phi)

    # Проверки
    if d is None or math.gcd(e, phi) != 1:
        st.error("⚠️ Ошибка: 'e' должно быть взаимно простым с (p-1)*(q-1). Поменяй 'e' или числа!")
    else:
        st.success(f"Ключи созданы! n = {n}, d = {d}")

        col_in, col_out = st.columns(2)

        with col_in:
            mode_rsa = st.radio("Действие:", ["Зашифровать текст", "Дешифровать числа"])
            input_rsa = st.text_area("Ввод данных (для дешифровки вводи числа через запятую):", key="rsa_input_new")

        if st.button("Запустить RSA процесс"):
            if mode_rsa == "Зашифровать текст":
                # Шифруем: (M^e) % n
                res = [pow(ord(c), e, n) for c in input_rsa]
                st.write("Зашифрованный список чисел:")
                st.code(", ".join(map(str, res)))
            else:
                # Дешифруем: (C^d) % n
                try:
                    nums = [int(x.strip()) for x in input_rsa.split(',')]
                    res = "".join([chr(pow(c, d, n)) for c in nums])
                    st.write("Расшифрованный текст:")
                    st.success(res)
                except Exception as err:
                    st.error("Ошибка! Проверь, что вводишь числа через запятую и они не больше n.")

        # Визуализация формул
        st.latex(rf"n = p \cdot q = {n}")
        st.latex(rf"\phi(n) = (p-1)(q-1) = {phi}")
        st.latex(rf"d \equiv {e}^{{-1}} \pmod{{{phi}}} = {d}")