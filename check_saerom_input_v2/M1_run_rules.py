import re
import pandas as pd

class NoMatchedExamError(Exception): pass
class NoAbnormalResultError(Exception): pass

def get_abnormal_list_by_date(
    df_raw: pd.DataFrame,
    target_columns: list[str],
    exclude_exact: list[str] | None = None,
    exclude_regex: list[str | re.Pattern] | None = None,
):
    """
    target_columns: 검사할 컬럼명 리스트
    exclude_exact: 값이 이 집합에 '정확히 일치'하면 제외 (공백 트림 후 비교)
    exclude_regex: 값에 '포함되면 제외'할 패턴들 (부분일치/정규식)
    """
    exclude_exact = {s.strip() for s in (exclude_exact or set())}

    # regex 준비 (문자열이면 컴파일)
    patterns = []
    for p in (exclude_regex or []):
        patterns.append(re.compile(p) if isinstance(p, str) else p)

    # 이용가능한 컬럼 확인
    available_cols = [c for c in target_columns if c in df_raw.columns]
    if not available_cols:
        raise NoMatchedExamError

    def _keep_value(v) -> bool:
        if pd.isna(v):
            return False
        s = str(v).strip()
        if not s:  # 빈 문자열
            return False
        if s in exclude_exact:  # exclue_exact와 일치하는 경우 제외
            return False
        for pat in patterns:  # exclude_regex에 의해 만들어진 patterns에 해당하면 제외
            if pat.search(s):
                return False
        return True

    # 여러 컬럼을 합쳐 하나의 통합 텍스트 만들기
    df = df_raw.copy()
    df["__통합특이사항__"] = (
        df[available_cols]
        .apply(lambda row: " / ".join([str(v) for v in row if _keep_value(v)]), axis=1)
        .replace("\n", " / ", regex=True)
    )

    # 내용 있는 행만
    df = df[df["__통합특이사항__"].astype(bool)]
    if df.empty:
        raise NoAbnormalResultError

    # 출력 포맷
    cols_needed = ["검진일자", "성명", "검진번호", "__통합특이사항__"]
    missing = [c for c in cols_needed if c not in df.columns]
    if missing:
        raise KeyError(f"필수 컬럼 누락: {missing}")

    df_print = df[cols_needed]
    abnormal_list = []
    for d in df_print["검진일자"].drop_duplicates().tolist():
        df_d = df_print[df_print["검진일자"] == d]
        lines = (df_d["성명"] + "(" + df_d["검진번호"].astype(str) + "): " + df_d["__통합특이사항__"]).tolist()
        abnormal_list.append(f" - {d}\n" + "\n".join(lines))

    return abnormal_list


def run_rules(df: pd.DataFrame, rules: dict):
    abnormal_list_concat = []
    missing_keys = []  # 대상 컬럼 자체가 없는 경우
    empty_keys = []    # 컬럼은 있으나 이상소견이 하나도 없는 경우

    for key, r in rules.items():
        df_to_use = r.get("data_filter", lambda x: x)(df)

        try:
            abnormal_list = get_abnormal_list_by_date(
                df_raw=df_to_use,
                target_columns=r["target_columns"],
                exclude_exact=r.get("exclude_exact"),
                exclude_regex=r.get("exclude_regex"),
            )

            abnormal_list_concat.append(f'* {key}\n' + '\n\n'.join(abnormal_list))
        
        except NoMatchedExamError:
            missing_keys.append(key)

        except NoAbnormalResultError:
            empty_keys.append(key)
        
    return abnormal_list_concat, missing_keys, empty_keys



if __name__ == '__main__':
    from M0_check_list import CHECK_RULES
    EXCEL_PATH = r"C:\Users\MyCom\Documents\통합 문서1.xlsx"
    df_raw = pd.read_excel(EXCEL_PATH, dtype={'챠트번호': str})

    abnormal_list, missing_keys, empty_keys = run_rules(df_raw, CHECK_RULES)
    if missing_keys: print(f'\n- 미실시 : {', '.join(missing_keys)}')
    if empty_keys: print(f'\n- 이상소견 없음 : {', '.join(empty_keys)}')
    print('\n'+'\n\n'.join(abnormal_list)+'\n')