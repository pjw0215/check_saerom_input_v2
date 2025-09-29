from setuptools import setup, find_packages

# requirements.txt 파일에서 의존성 읽기
with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name='check_saerom_input_v2',
    version='0.1.0',
    packages=find_packages(),  # 현재 폴더 내 __init__.py 있는 모든 디렉토리 포함
    install_requires=requirements,
    author='Your Name',
    author_email='your@email.com',
    description='Custom utility modules by JW',
    url='https://github.com/your-username/check_saerom_input_v2',  # 필요시 수정
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',  # 필요에 따라 수정
)