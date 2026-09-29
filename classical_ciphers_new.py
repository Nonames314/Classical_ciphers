"""
Classical Cipher Suite - Desktop GUI App
6 phương pháp mã hóa cổ điển: Caesar, Monoalphabetic, Vigenère, Playfair, OTP, Rail Fence
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import string
import random
import math


# ─────────────────────────────────────────────────────────────
#  CIPHER IMPLEMENTATIONS
# ─────────────────────────────────────────────────────────────

class CaesarCipher:
    """
    Mã Caesar: dịch chuyển mỗi ký tự trong bảng chữ cái đi k vị trí.
    Công thức: E(x) = (x + k) mod 26  |  D(x) = (x - k) mod 26
    Khóa K: số nguyên (ví dụ: 3)
    """
    @staticmethod
    def process(text: str, key: str, encrypt: bool) -> str:
        try:
            shift = int(key) % 26
        except ValueError:
            raise ValueError("Khóa Caesar phải là số nguyên (ví dụ: 3)")
        if not encrypt:
            shift = -shift
        result = []
        for ch in text:
            if ch.isalpha():
                base = ord('A') if ch.isupper() else ord('a')
                result.append(chr((ord(ch) - base + shift) % 26 + base))
            else:
                result.append(ch)
        return ''.join(result)


class MonoalphabeticCipher:
    """
    Mã đơn bảng: ánh xạ mỗi chữ cái sang một chữ cái khác theo bảng thay thế.
    Khóa K: 26 ký tự duy nhất (hoán vị của bảng chữ cái), ví dụ: QWERTYUIOPASDFGHJKLZXCVBNM
    """
    @staticmethod
    def _build_table(key: str):
        key = key.upper()
        if len(key) != 26 or not all(c in string.ascii_uppercase for c in key) or len(set(key)) != 26:
            raise ValueError("Khóa Monoalphabetic phải là 26 ký tự A-Z duy nhất\n"
                             "Ví dụ: QWERTYUIOPASDFGHJKLZXCVBNM")
        enc = {string.ascii_uppercase[i]: key[i] for i in range(26)}
        dec = {v: k for k, v in enc.items()}
        return enc, dec

    @staticmethod
    def process(text: str, key: str, encrypt: bool) -> str:
        enc, dec = MonoalphabeticCipher._build_table(key.strip())
        table = enc if encrypt else dec
        result = []
        for ch in text:
            upper = ch.upper()
            if upper in table:
                mapped = table[upper]
                result.append(mapped if ch.isupper() else mapped.lower())
            else:
                result.append(ch)
        return ''.join(result)


class VigenereCipher:
    """
    Mã Vigenère: dùng từ khóa lặp lại để mã hóa, mỗi ký tự dùng dịch chuyển khác nhau.
    Công thức: E(i) = (M[i] + K[i mod len(K)]) mod 26
    Khóa K: chuỗi chữ cái (ví dụ: KEY)
    """
    @staticmethod
    def process(text: str, key: str, encrypt: bool) -> str:
        key = key.upper()
        if not key.isalpha():
            raise ValueError("Khóa Vigenère chỉ được chứa chữ cái (ví dụ: KEY)")
        result = []
        ki = 0
        for ch in text:
            if ch.isalpha():
                shift = ord(key[ki % len(key)]) - ord('A')
                if not encrypt:
                    shift = -shift
                base = ord('A') if ch.isupper() else ord('a')
                result.append(chr((ord(ch) - base + shift) % 26 + base))
                ki += 1
            else:
                result.append(ch)
        return ''.join(result)


class PlayfairCipher:
    """
    Mã Playfair: mã hóa từng cặp ký tự (bigram) trên ma trận 5x5.
    - Tạo ma trận 5x5 từ khóa (I và J dùng chung ô).
    - Quy tắc: cùng hàng → dịch phải; cùng cột → dịch xuống; khác → hoán góc chéo.
    Khóa K: chuỗi chữ cái (ví dụ: MONARCHY)
    """
    @staticmethod
    def _build_matrix(key: str):
        key = key.upper().replace('J', 'I')
        seen = set()
        order = []
        for ch in key + string.ascii_uppercase:
            if ch == 'J':
                continue
            if ch not in seen:
                seen.add(ch)
                order.append(ch)
        matrix = [order[i*5:(i+1)*5] for i in range(5)]
        pos = {ch: (r, c) for r, row in enumerate(matrix) for c, ch in enumerate(row)}
        return matrix, pos

    @staticmethod
    def _prepare_text(text: str) -> str:
        text = text.upper().replace('J', 'I')
        text = ''.join(ch for ch in text if ch.isalpha())
        pairs = []
        i = 0
        while i < len(text):
            a = text[i]
            if i + 1 < len(text):
                b = text[i + 1]
                if a == b:
                    pairs.append(a + 'X')
                    i += 1
                else:
                    pairs.append(a + b)
                    i += 2
            else:
                pairs.append(a + 'X')
                i += 1
        return ''.join(pairs)

    @staticmethod
    def process(text: str, key: str, encrypt: bool) -> str:
        if not key.isalpha():
            raise ValueError("Khóa Playfair chỉ được chứa chữ cái (ví dụ: MONARCHY)")
        matrix, pos = PlayfairCipher._build_matrix(key.strip())
        prepared = PlayfairCipher._prepare_text(text)
        step = 1 if encrypt else -1
        result = []
        for i in range(0, len(prepared), 2):
            a, b = prepared[i], prepared[i+1]
            r1, c1 = pos[a]
            r2, c2 = pos[b]
            if r1 == r2:
                result.append(matrix[r1][(c1 + step) % 5])
                result.append(matrix[r2][(c2 + step) % 5])
            elif c1 == c2:
                result.append(matrix[(r1 + step) % 5][c1])
                result.append(matrix[(r2 + step) % 5][c2])
            else:
                result.append(matrix[r1][c2])
                result.append(matrix[r2][c1])
        return ''.join(result)


class OTPCipher:
    """
    One-Time Pad (OTP): cộng/trừ từng chữ cái với khóa cùng độ dài theo mod 26.
    - Chỉ hoạt động trên 26 chữ cái tiếng Anh hoa.
    - Khóa phải là chuỗi chữ cái, dài ≥ số chữ cái trong bản tin.
    - Công thức: E(i) = (M[i] + K[i]) mod 26  |  D(i) = (C[i] - K[i]) mod 26
    Khóa K: chuỗi chữ cái A-Z (ví dụ: XMCKL)
    """
    @staticmethod
    def process(text: str, key: str, encrypt: bool) -> str:
        key = key.upper()
        if not key.isalpha():
            raise ValueError("Khóa OTP chỉ được chứa chữ cái A-Z (ví dụ: XMCKL)")
        # Chỉ đếm số chữ cái trong bản tin
        alpha_count = sum(1 for ch in text if ch.upper().isalpha())
        if len(key) < alpha_count:
            raise ValueError(f"Khóa OTP phải dài ít nhất {alpha_count} ký tự\n"
                             f"(bản tin có {alpha_count} chữ cái, khóa chỉ {len(key)} ký tự)")
        result = []
        ki = 0
        for ch in text:
            upper = ch.upper()
            if upper.isalpha():
                shift = ord(key[ki]) - ord('A')
                if not encrypt:
                    shift = -shift
                encrypted = chr((ord(upper) - ord('A') + shift) % 26 + ord('A'))
                result.append(encrypted)
                ki += 1
            else:
                result.append(ch)
        return ''.join(result)


class RailFenceCipher:
    """
    Mã hàng rào sắt (Rail Fence): viết bản tin theo đường ziczac qua các hàng,
    sau đó đọc từng hàng để tạo bản mã.
    Khóa K: số hàng (ví dụ: 3)
    """
    @staticmethod
    def process(text: str, key: str, encrypt: bool) -> str:
        try:
            rails = int(key)
            if rails < 2:
                raise ValueError
        except ValueError:
            raise ValueError("Khóa Rail Fence phải là số nguyên ≥ 2 (ví dụ: 3)")

        n = len(text)
        if encrypt:
            fence = [[] for _ in range(rails)]
            for i, ch in enumerate(text):
                fence[i % rails].append(ch)
            return ''.join(''.join(r) for r in fence)
        else:
            lengths = [0] * rails
            for i in range(n):
                lengths[i % rails] += 1
            fence = []
            idx = 0
            for length in lengths:
                fence.append(list(text[idx:idx + length]))
                idx += length
            pointers = [0] * rails
            result = []
            for i in range(n):
                rail = i % rails
                result.append(fence[rail][pointers[rail]])
                pointers[rail] += 1
            return ''.join(result)


# ─────────────────────────────────────────────────────────────
#  GUI APPLICATION
# ─────────────────────────────────────────────────────────────

CIPHERS = {
    "🔐  Caesar Cipher": {
        "cls": CaesarCipher,
        "key_hint": "Số nguyên, ví dụ: 3",
        "desc": (
            "Dịch chuyển mỗi ký tự đi K vị trí trong bảng chữ cái.\n"
            "E(x) = (x + K) mod 26   |   Khóa: số nguyên (vd: 3)"
        ),
        "color": "#4f8ef7",
    },
    "🔑  Monoalphabetic": {
        "cls": MonoalphabeticCipher,
        "key_hint": "26 ký tự A-Z duy nhất, vd: QWERTYUIOPASDFGHJKLZXCVBNM",
        "desc": (
            "Thay thế mỗi chữ cái bằng chữ cái tương ứng trong bảng hoán vị 26 ký tự.\n"
            "Khóa: chuỗi 26 ký tự A-Z không trùng (vd: QWERTYUIOPASDFGHJKLZXCVBNM)"
        ),
        "color": "#e06c75",
    },
    "🗝️  Vigenère Cipher": {
        "cls": VigenereCipher,
        "key_hint": "Chuỗi chữ cái, vd: KEY",
        "desc": (
            "Dùng từ khóa lặp lại, mỗi ký tự dùng dịch chuyển riêng.\n"
            "E(i) = (M[i] + K[i mod |K|]) mod 26   |   Khóa: chữ cái (vd: KEY)"
        ),
        "color": "#98c379",
    },
    "♟️  Playfair Cipher": {
        "cls": PlayfairCipher,
        "key_hint": "Chuỗi chữ cái, vd: MONARCHY",
        "desc": (
            "Mã hóa từng cặp ký tự (bigram) trên ma trận 5×5, I=J.\n"
            "Khóa: chuỗi chữ cái tạo ma trận (vd: MONARCHY)"
        ),
        "color": "#e5c07b",
    },
    "🎲  One-Time Pad": {
        "cls": OTPCipher,
        "key_hint": "Chuỗi chữ cái A-Z, độ dài ≥ số chữ cái bản tin",
        "desc": (
            "Cộng/trừ từng chữ cái với khóa theo mod 26 — tuyệt đối an toàn.\n"
            "E(i) = (M[i] + K[i]) mod 26  |  Khóa: chuỗi chữ cái A-Z ≥ |M|"
        ),
        "color": "#c678dd",
    },
    "🚧  Rail Fence Cipher": {
        "cls": RailFenceCipher,
        "key_hint": "Số hàng nguyên ≥ 2, vd: 3",
        "desc": (
            "Viết bản tin theo đường ziczac qua K hàng, đọc từng hàng làm bản mã.\n"
            "Khóa: số hàng nguyên ≥ 2 (vd: 3)"
        ),
        "color": "#56b6c2",
    },
}

DARK_BG   = "#1e2127"
PANEL_BG  = "#282c34"
CARD_BG   = "#2c313a"
TEXT_FG   = "#abb2bf"
WHITE_FG  = "#dcdfe4"
BORDER    = "#3e4452"
ACCENT    = "#61afef"

BTN_ENC   = "#4f8ef7"
BTN_DEC   = "#56b6c2"
BTN_CLR   = "#e06c75"
BTN_COPY  = "#98c379"


class ClassicalCipherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Classical Cipher Suite")
        self.configure(bg=DARK_BG)
        self.resizable(True, True)
        self.minsize(860, 640)

        self._selected_cipher = tk.StringVar(value=list(CIPHERS.keys())[0])
        self._mode = tk.StringVar(value="encrypt")

        self._setup_fonts()
        self._build_ui()
        self._on_cipher_change()

        # Center window
        self.update_idletasks()
        w, h = 980, 720
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_fonts(self):
        self.f_title  = ("Courier New", 18, "bold")
        self.f_sub    = ("Courier New", 10)
        self.f_label  = ("Consolas", 10, "bold")
        self.f_hint   = ("Consolas", 9)
        self.f_text   = ("Consolas", 11)
        self.f_desc   = ("Consolas", 9)
        self.f_btn    = ("Consolas", 10, "bold")
        self.f_cipher = ("Consolas", 10)

    def _styled_frame(self, parent, bg=PANEL_BG, bd=0, **kw):
        return tk.Frame(parent, bg=bg, bd=bd, **kw)

    def _label(self, parent, text, fg=TEXT_FG, font=None, bg=None, **kw):
        return tk.Label(parent, text=text, fg=fg,
                        font=font or self.f_label,
                        bg=bg or parent.cget("bg"), **kw)

    def _button(self, parent, text, cmd, color, width=14):
        btn = tk.Button(
            parent, text=text, command=cmd,
            bg=color, fg="#1e2127", activebackground=color,
            activeforeground="#1e2127", relief="flat",
            font=self.f_btn, cursor="hand2",
            width=width, pady=6,
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=self._lighten(color)))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    @staticmethod
    def _lighten(hex_color, amount=30):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = min(255, r + amount)
        g = min(255, g + amount)
        b = min(255, b + amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────
        header = self._styled_frame(self, bg=DARK_BG)
        header.pack(fill="x", padx=20, pady=(16, 4))

        self._label(header, "⚙  CLASSICAL CIPHER SUITE",
                    fg=WHITE_FG, font=self.f_title).pack(side="left")
        self._label(header, "6 phương pháp mã hóa cổ điển",
                    fg=TEXT_FG, font=self.f_sub).pack(side="left", padx=16, pady=(6, 0))

        # ── Main layout ─────────────────────────────────────────
        main = self._styled_frame(self, bg=DARK_BG)
        main.pack(fill="both", expand=True, padx=20, pady=8)
        main.columnconfigure(0, weight=0, minsize=200)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # Left sidebar: cipher selector
        self._build_sidebar(main)

        # Right panel: input/output
        self._build_main_panel(main)

    def _build_sidebar(self, parent):
        sidebar = self._styled_frame(parent, bg=PANEL_BG)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self._label(sidebar, "  PHƯƠNG PHÁP", fg=ACCENT,
                    font=("Consolas", 9, "bold")).pack(anchor="w", pady=(10, 4), padx=8)

        self._cipher_buttons = {}
        for name in CIPHERS:
            color = CIPHERS[name]["color"]
            btn = tk.Radiobutton(
                sidebar, text=name,
                variable=self._selected_cipher, value=name,
                command=self._on_cipher_change,
                bg=PANEL_BG, fg=TEXT_FG,
                selectcolor=CARD_BG,
                activebackground=CARD_BG,
                activeforeground=WHITE_FG,
                font=self.f_cipher,
                relief="flat", cursor="hand2",
                indicatoron=False,
                anchor="w", padx=12, pady=8,
                width=22,
            )
            btn.pack(fill="x", padx=4, pady=1)
            self._cipher_buttons[name] = (btn, color)

        # Separator
        sep = tk.Frame(sidebar, bg=BORDER, height=1)
        sep.pack(fill="x", padx=8, pady=10)

        # Generate random key button
        self._label(sidebar, "  CÔNG CỤ", fg=ACCENT,
                    font=("Consolas", 9, "bold")).pack(anchor="w", pady=(0, 4), padx=8)

        gen_btn = tk.Button(
            sidebar, text="🎲 Tạo khóa ngẫu nhiên",
            command=self._generate_key,
            bg=CARD_BG, fg=TEXT_FG,
            activebackground=BORDER, activeforeground=WHITE_FG,
            relief="flat", font=self.f_hint, cursor="hand2",
            padx=12, pady=6, anchor="w",
        )
        gen_btn.pack(fill="x", padx=4, pady=1)

        clr_btn = tk.Button(
            sidebar, text="🗑  Xóa tất cả",
            command=self._clear_all,
            bg=CARD_BG, fg=TEXT_FG,
            activebackground=BORDER, activeforeground=WHITE_FG,
            relief="flat", font=self.f_hint, cursor="hand2",
            padx=12, pady=6, anchor="w",
        )
        clr_btn.pack(fill="x", padx=4, pady=1)

    def _build_main_panel(self, parent):
        panel = self._styled_frame(parent, bg=DARK_BG)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)
        panel.rowconfigure(4, weight=1)

        # ── Description card ───────────────────────────────────
        self._desc_var = tk.StringVar()
        desc_card = self._styled_frame(panel, bg=CARD_BG)
        desc_card.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self._desc_lbl = tk.Label(
            desc_card, textvariable=self._desc_var,
            fg="#5c6370", font=self.f_desc,
            bg=CARD_BG, justify="left", anchor="w",
            wraplength=640, padx=12, pady=8,
        )
        self._desc_lbl.pack(fill="x")

        # ── Key row ────────────────────────────────────────────
        key_row = self._styled_frame(panel, bg=DARK_BG)
        key_row.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        key_row.columnconfigure(1, weight=1)

        self._label(key_row, "KHÓA K:", fg=ACCENT).grid(row=0, column=0, padx=(0, 8))
        self._key_entry = tk.Entry(
            key_row, bg=CARD_BG, fg=WHITE_FG, insertbackground=WHITE_FG,
            relief="flat", font=self.f_text, bd=0,
        )
        self._key_entry.grid(row=0, column=1, sticky="ew", ipady=6, padx=(0, 8))

        self._hint_var = tk.StringVar()
        tk.Label(key_row, textvariable=self._hint_var,
                 fg="#5c6370", font=self.f_hint,
                 bg=DARK_BG).grid(row=0, column=2)

        # ── Message (input) ────────────────────────────────────
        self._label(panel, "BẢN TIN M  (nhập vào):",
                    fg=TEXT_FG).grid(row=2, column=0, sticky="nw", pady=(0, 2))

        msg_frame = self._styled_frame(panel, bg=CARD_BG)
        msg_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 8))  # fixed height
        msg_frame.rowconfigure(0, weight=1)
        msg_frame.columnconfigure(0, weight=1)

        self._msg_text = tk.Text(
            msg_frame, bg=CARD_BG, fg=WHITE_FG, insertbackground=WHITE_FG,
            relief="flat", font=self.f_text, bd=0,
            wrap="word", height=6,
            selectbackground=ACCENT, selectforeground=DARK_BG,
        )
        self._msg_text.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        msg_scroll = ttk.Scrollbar(msg_frame, orient="vertical",
                                   command=self._msg_text.yview)
        msg_scroll.grid(row=0, column=1, sticky="ns")
        self._msg_text.config(yscrollcommand=msg_scroll.set)

        # ── Action buttons ─────────────────────────────────────
        btn_row = self._styled_frame(panel, bg=DARK_BG)
        btn_row.grid(row=4, column=0, sticky="ew", pady=4)

        self._button(btn_row, "🔒  MÃ HÓA", self._encrypt, BTN_ENC).pack(side="left", padx=(0, 8))
        self._button(btn_row, "🔓  GIẢI MÃ", self._decrypt, BTN_DEC).pack(side="left", padx=(0, 8))
        self._button(btn_row, "📋  Sao chép KQ", self._copy_result, BTN_COPY, width=16).pack(side="left", padx=(0, 8))
        self._button(btn_row, "⇅  Hoán đổi", self._swap, "#e5c07b", width=12).pack(side="left")

        # ── Result (output) ────────────────────────────────────
        out_row = self._styled_frame(panel, bg=DARK_BG)
        out_row.grid(row=5, column=0, sticky="ew", pady=(8, 2))
        out_row.columnconfigure(0, weight=1)

        self._label(out_row, "KẾT QUẢ  (đầu ra):",
                    fg=TEXT_FG).grid(row=0, column=0, sticky="w")
        self._status_var = tk.StringVar(value="")
        self._status_lbl = tk.Label(
            out_row, textvariable=self._status_var,
            fg="#98c379", font=self.f_hint, bg=DARK_BG,
        )
        self._status_lbl.grid(row=0, column=1, sticky="e")

        res_frame = self._styled_frame(panel, bg=CARD_BG)
        res_frame.grid(row=6, column=0, sticky="nsew", pady=(0, 4))
        res_frame.rowconfigure(0, weight=1)
        res_frame.columnconfigure(0, weight=1)
        panel.rowconfigure(6, weight=1)

        self._res_text = tk.Text(
            res_frame, bg=CARD_BG, fg="#98c379", insertbackground="#98c379",
            relief="flat", font=self.f_text, bd=0,
            wrap="word", height=6,
            selectbackground=ACCENT, selectforeground=DARK_BG,
            state="disabled",
        )
        self._res_text.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        res_scroll = ttk.Scrollbar(res_frame, orient="vertical",
                                   command=self._res_text.yview)
        res_scroll.grid(row=0, column=1, sticky="ns")
        self._res_text.config(yscrollcommand=res_scroll.set)

        # Style scrollbars
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar",
                        background=BORDER, troughcolor=CARD_BG,
                        arrowcolor=TEXT_FG, bordercolor=CARD_BG)

    # ── Events ──────────────────────────────────────────────────

    def _on_cipher_change(self):
        name = self._selected_cipher.get()
        info = CIPHERS[name]
        self._hint_var.set(f"  ←  {info['key_hint']}")
        self._desc_var.set(info["desc"])

        # Update radio button styles
        for n, (btn, col) in self._cipher_buttons.items():
            if n == name:
                btn.config(fg=col, bg=CARD_BG, font=("Consolas", 10, "bold"))
            else:
                btn.config(fg=TEXT_FG, bg=PANEL_BG, font=self.f_cipher)

        self._status_var.set("")

    def _get_inputs(self):
        msg = self._msg_text.get("1.0", "end-1c")
        key = self._key_entry.get()
        if not msg.strip():
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập bản tin M.")
            return None, None
        if not key.strip():
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập khóa K.")
            return None, None
        return msg, key

    def _run(self, encrypt: bool):
        msg, key = self._get_inputs()
        if msg is None:
            return
        name = self._selected_cipher.get()
        cls = CIPHERS[name]["cls"]
        try:
            result = cls.process(msg, key, encrypt)
            self._set_result(result)
            mode = "✅ Mã hóa" if encrypt else "✅ Giải mã"
            self._status_var.set(f"{mode} thành công  ({len(result)} ký tự)")
            self._status_lbl.config(fg="#98c379")
        except ValueError as e:
            messagebox.showerror("Lỗi khóa / dữ liệu", str(e))
            self._status_var.set("❌ Lỗi")
            self._status_lbl.config(fg=BTN_CLR)
        except Exception as e:
            messagebox.showerror("Lỗi không xác định", str(e))

    def _encrypt(self):
        self._run(encrypt=True)

    def _decrypt(self):
        self._run(encrypt=False)

    def _set_result(self, text: str):
        self._res_text.config(state="normal")
        self._res_text.delete("1.0", "end")
        self._res_text.insert("end", text)
        self._res_text.config(state="disabled")

    def _copy_result(self):
        result = self._res_text.get("1.0", "end-1c")
        if not result.strip():
            messagebox.showinfo("Thông báo", "Chưa có kết quả để sao chép.")
            return
        self.clipboard_clear()
        self.clipboard_append(result)
        self._status_var.set("📋 Đã sao chép vào clipboard!")
        self._status_lbl.config(fg="#e5c07b")

    def _swap(self):
        """Chuyển kết quả xuống thành đầu vào (tiện dùng chuỗi mã hóa/giải mã liên tiếp)."""
        result = self._res_text.get("1.0", "end-1c")
        if not result.strip():
            return
        self._msg_text.delete("1.0", "end")
        self._msg_text.insert("end", result)
        self._set_result("")
        self._status_var.set("⇅ Đã hoán đổi đầu vào / đầu ra")
        self._status_lbl.config(fg="#e5c07b")

    def _clear_all(self):
        self._msg_text.delete("1.0", "end")
        self._key_entry.delete(0, "end")
        self._set_result("")
        self._status_var.set("")

    def _generate_key(self):
        name = self._selected_cipher.get()
        self._key_entry.delete(0, "end")
        if "Caesar" in name:
            self._key_entry.insert(0, str(random.randint(1, 25)))
        elif "Monoalphabetic" in name:
            alpha = list(string.ascii_uppercase)
            random.shuffle(alpha)
            self._key_entry.insert(0, ''.join(alpha))
        elif "Vigenère" in name:
            length = random.randint(4, 8)
            self._key_entry.insert(0, ''.join(random.choices(string.ascii_uppercase, k=length)))
        elif "Playfair" in name:
            length = random.randint(5, 10)
            self._key_entry.insert(0, ''.join(random.choices(string.ascii_uppercase, k=length)))
        elif "One-Time" in name:
            msg = self._msg_text.get("1.0", "end-1c")
            alpha_count = sum(1 for ch in msg if ch.upper().isalpha())
            n = max(alpha_count, 16)
            self._key_entry.insert(0, ''.join(random.choices(string.ascii_uppercase, k=n)))
        elif "Rail" in name:
            self._key_entry.insert(0, str(random.randint(2, 5)))


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ClassicalCipherApp()
    app.mainloop()
