import streamlit as st
import math

# --- МОДЕЛИ (ЛОГИКА ШИФРОВАНИЯ) ---

class CaesarCipher:
    """Класс для работы с шифром Цезаря."""
    @staticmethod
    def process(text: str, shift: int, mode: str = 'enc') -> str:
        result = ""
        s = shift if mode == 'enc' else -shift
        for char in text:
            new_code = ord(char) + s
            result += chr(new_code)
        return result


class XorCipher:
    """Класс для работы с XOR шифрованием."""
    @staticmethod
    def process(text: str, key: str) -> str:
        result = ""
        for i in range(len(text)):
            result += chr(ord(text[i]) ^ ord(key[i % len(key)]))
        return result


class RsaCipher:
    """Класс для математики и шифрования алгоритма RSA."""
    @staticmethod
    def _iterative_egcd(a: int, b: int):
        x, y, u, v = 0, 1, 1, 0
        while a != 0:
            q, r = b // a, b % a
            m, n = x - u * q, y - v * q
            b, a, x, y, u, v = a, r, u, v, m, n
        return b, x, y

    @classmethod
    def mod_inverse(cls, e: int, phi: int):
        g, x, y = cls._iterative_egcd(e, phi)
        if g != 1:
            return None
        else:
            return x % phi

    @staticmethod
    def encrypt(text: str, e: int, n: int) -> list:
        return [pow(ord(c), e, n) for c in text]

    @staticmethod
    def decrypt(nums: list, d: int, n: int) -> str:
        return "".join([chr(pow(c, d, n)) for c in nums])


# --- ПРЕДСТАВЛЕНИЕ И КОНТРОЛЛЕР (ИНТЕРФЕЙС APP) ---

class CryptoApp:
    """Главный класс приложения для управления интерфейсом Streamlit."""
    def __init__(self):
        self.title = "Сервис быстрого шифрования"

    def setup_page(self):
        """Настройка конфигурации и стилей страницы."""
        st.set_page_config(page_title="Криптошифр", layout="centered")
        
        # Кастомный CSS
        st.markdown("""
            <style>
            .main { background-color: #0e1117; }
            .stTextInput, .stTextArea, .stNumberInput { border-radius: 10px !important; }
            .stButton>button { width: 100%; border-radius: 20px; background: linear-gradient(45deg, #00f2fe 0%, #4facfe 100%); color: white; border: none; }
            .result-box { padding: 20px; border-radius: 15px; background-color: #1e2130; border-left: 5px solid #4facfe; font-family: 'Courier New', monospace; }
            </style>
            """, unsafe_allow_html=True)

    def render_header(self):
        """Отрисовка заголовков приложения."""
        st.title(self.title)
        st.write("Используйте на свое усмотрение мы не несем отвественности ни за что")

    def render_caesar_tab(self):
        """Вкладка Шифра Цезаря."""
        st.subheader("Шифр Цезаря")
        c_mode = st.radio("Режим:", ["Зашифровать", "Расшифровать"], key="c_mode_choice")

        col1, col2 = st.columns([2, 1])
        with col1:
            msg = st.text_area("Текст:", placeholder="Введите текст сюда...", key="c_msg")
        with col2:
            shift = st.number_input("Сдвиг (ключ):", value=3, step=1, key="c_shift_val")

        if st.button("Выполнить преобразование"):
            mode_flag = 'enc' if c_mode == "Зашифровать" else 'dec'
            res = CaesarCipher.process(msg, shift, mode_flag)
            
            if c_mode == "Зашифровать":
                st.write("Результат (копируй это):")
                st.code(res)
            else:
                st.write("Расшифрованный текст:")
                st.success(res)

    def render_xor_tab(self):
        """Вкладка XOR шифрования."""
        st.subheader("XOR Шифрование (Биты)")
        msg_xor = st.text_input("Текст для XOR:", key="x_msg")
        key_xor = st.text_input("Ключ (слово):", value="KEY", key="x_key")

        if st.button("Выполнить XOR преобразование"):
            res = XorCipher.process(msg_xor, key_xor)
            st.markdown("**Результат (в символах):**")
            st.code(res)
            st.markdown("**Результат (в битах):**")
            st.write(" ".join(format(ord(c), '08b') for c in res))

    def render_rsa_tab(self):
        """Вкладка Конструктора RSA."""
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
        d = RsaCipher.mod_inverse(e, phi)

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
                    res = RsaCipher.encrypt(input_rsa, e, n)
                    st.write("Зашифрованный список чисел:")
                    st.code(", ".join(map(str, res)))
                else:
                    try:
                        nums = [int(x.strip()) for x in input_rsa.split(',')]
                        res = RsaCipher.decrypt(nums, d, n)
                        st.write("Расшифрованный текст:")
                        st.success(res)
                    except Exception as err:
                        st.error("Ошибка! Проверь, что вводишь числа через запятую и они не больше n.")

            # Визуализация формул
            st.latex(rf"n = p \cdot q = {n}")
            st.latex(rf"\phi(n) = (p-1)(q-1) = {phi}")
            st.latex(rf"d \equiv {e}^{{-1}} \pmod{{{phi}}} = {d}")

    def run(self):
        """Запуск всего жизненного цикла приложения."""
        self.setup_page()
        self.render_header()
        
        # Создание вкладок
        tab1, tab2, tab3 = st.tabs(["Цезарь", "XOR Логика", "Baby-RSA"])
        
        with tab1:
            self.render_caesar_tab()
        with tab2:
            self.render_xor_tab()
        with tab3:
            self.render_rsa_tab()


# --- ТОЧКА ВХОДА ---
if __name__ == "__main__":
    app = CryptoApp()
    app.run()
