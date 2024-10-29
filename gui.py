import streamlit as st
from PIL import Image
from typing import Any
import numpy as np
import io

class GUI:
    def __init__(self)->None:
        if 'configs' not in st.session_state:
            st.session_state.configs = {
                "lora": None,
                "prompt": "",
                "batch_count":1,
                "gim1": None,
                "gim2": None
            }
        
        if 'outputs' not in st.session_state:
            st.session_state.outputs = []  # List[Image.Image]

        # self.output_placeholder = st.empty  # 초기화

        self.__loras = ("Harry Potter")
        app = self.__gui_main() # Main GUI

    def __clear_form(self):
        st.session_state.configs = {
            "lora": None,
            "prompt": "",
            "batch_count":1,
            "gim1": None,
            "gim2": None
        }
        st.session_state.lora = None
        st.session_state.prompt = ""
        st.session_state.bc = 1

    def __gui_main(self)->Any:
        with st.container(key="app") as app:
            st.header("🔥 Demo")
            self.__gui_lora()
            self.__gui_input()

            btn_act = True
            btn_act = len(st.session_state.outputs) == 0  # Disable button if outputs are present
            st.button(label="결과보기", on_click=self.__gui_output, disabled=btn_act)

            self.output_placeholder = st.container() # 결과물
        return app
    
    def __gui_lora(self)->Any:
        with st.container() as con:
            st.session_state.configs['lora'] = st.selectbox(label="작품을 선택해주세요.",key="lora",options=self.__loras,index=None,placeholder="여기서 작품을 선택하세요. 검색도 가능")
        return con
    
    def __gui_input(self)->Any:
        with st.container(border=True) as con:
            st.markdown("""
### 입력방법
1. **Prompt**만 입력
2. **Guide Image**만 입력
3. **Prompt**와 **Guide Image** 같이 입력
""")
            # Prompt
            prompt = st.text_input(label="👨🏻‍💻 **Prompt** 입력",key="prompt",placeholder="여기에 프롬프트를 입력해주세요!")
            if prompt != "":
                st.session_state.configs['prompt'] = prompt
            batch_count = st.number_input(label="몇장 생성하실껀가요?(1~60), 제대로 설정안하면 1로 설정",key="bc",value=1,min_value=1,max_value=60)
            st.session_state.configs['batch_count'] = batch_count
            # Guide Image 1 : 콘티
            gimg1 = st.file_uploader("🎨 **콘티 이미지**: PNG 또는 JPG 이미지를 업로드하세요",key="gim1", type=["png", "jpg", "jpeg"])
            if gimg1 is not None:
                st.session_state.configs['gim1'] = Image.open(gimg1)
                st.image(st.session_state.configs['gim1'], width=100,caption="콘티 이미지", use_column_width=True)
            else:
                st.session_state.configs['gim1'] = None
            # Guide Image 2 : 포즈
            gimg2 = st.file_uploader("🕺🏼 **포즈 이미지**: PNG 또는 JPG 이미지를 업로드하세요",key="gim2", type=["png", "jpg", "jpeg"])
            if gimg2 is not None:
                st.session_state.configs['gim2'] = Image.open(gimg2)
                st.image(st.session_state.configs['gim2'], width=100, caption="포즈 이미지", use_column_width=True)
            else:
                st.session_state.configs['gim2'] = None
            btn1, btn2 = st.columns([1, 1],gap="small",vertical_alignment="bottom")
            
            btn_activate = True
            self.__flow()
            with btn1:
                if st.session_state.configs['lora'] is not None and (
                    st.session_state.configs['prompt'] != "" or 
                    st.session_state.configs['gim1'] is not None or 
                    st.session_state.configs['gim2'] is not None):
                    btn_activate = False

                submit = st.button("이미지 생성",type="primary",disabled=btn_activate)
                if submit: # 이미지 처리
                    bar = st.progress(0,text="이미지 생성 시작")
                    import time
                    time.sleep(2)
                    bar.progress(10,text="베이스 모델 초기화")
                    time.sleep(2)
                    bar.progress(35,text="LoRA 연결")
                    time.sleep(2)
                    start = 35
                    if st.session_state.configs['gim1'] is not None or st.session_state.configs['gim1'] is not None:
                        bar.progress(40,text="ControlNet 연결")
                        start = 40
                    time.sleep(2)
                    for per in range(start,100+1):
                        time.sleep(0.05)
                        bar.progress(per,text="이미지 생성 중입니다.")

                    bar.empty() # bar 없애기
                
                    self.__pipe(self.__flow(),st.session_state.configs["batch_count"]) # 결과 보이기
            with btn2: # 현재 로직상 업로드 파일은 클리어가 안됨
                st.button("Clear",on_click=self.__clear_form)

        return con

    def __flow(self)->int:
        # ['lora', 'prompt', 'batch_count', 'gim1', 'gim2']
        configs = st.session_state.configs
        configs = (configs['prompt'],configs['gim1'],configs['gim2'])
        checks = None
        # 1. prompt만
        if configs[0] != '' and (configs[1] is None and configs[2] is None):
            checks = 0
        # 2. Guide 이미지만(콘티)
        elif configs[1] is not None and (configs[0] == "" and configs[2] is None):
            checks = 1
        # 3. Guide 이미지만(포즈)
        elif configs[2] is not None and (configs[0] == "" and configs[1] is None):
            checks = 2
        # 4. Guide 이미지만(콘티, 포즈)
        elif (configs[1] is not None and configs[2] is not None) and configs[0] == "":
            checks = 3
        # 5. Guide 이미지 + prompt 
        else:
            checks = 4
        return checks

    def __pipe(self,type:int,bc:int)->Any:
        counts = np.random.choice(range(10),bc)

        st.session_state.outputs = [Image.open(f"./images/{type}/{img}.png") for img in counts]
    
    def __gui_output(self)->Any:
        with self.output_placeholder:
            # 그리드 형식으로 이미지 표시
            columns = 3  # 한 행에 표시할 열의 수
            num_columns = min(columns, len(st.session_state.outputs))  # 실제 열의 수 조정

            # 열 생성
            cols = st.columns(num_columns)

            for i, img in enumerate(st.session_state.outputs):
                with cols[i % num_columns]:  # 각 열에 이미지 배치
                    st.image(img, use_column_width=True, caption=f"이미지 {i + 1}")
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    buf.seek(0)

                    st.download_button(
                        label="✅ Download",
                        data=buf,
                        file_name=f"image_{i + 1}.png",
                        mime="image/png",
                    )
        return self.output_placeholder

if __name__ == "__main__":
    GUI()