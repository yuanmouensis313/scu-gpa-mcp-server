#!/usr/bin/env python3
"""
四川大学本科生课程成绩与绩点核算MCP服务器
完全复刻Java版GPA_Application核心逻辑，严格遵循川大十二级绩点官方标准
"""
import json
from typing import Dict, Any, List
from hello_agents.protocols import MCPServer

# ===================== 1. 核心绩点计算逻辑 =====================
class SCUGPACalculator:
    """四川大学绩点计算核心类，完全对齐Java版GPAUtils/GPACalculator逻辑"""
    # 静态常量
    MAX_GPA = 4.0
    MIN_GPA = 0.0
    PASS_SCORE = 60

    @classmethod
    def calc_gpa_by_score(cls, score: int) -> float:
        """百分制成绩转绩点，严格遵循川大官方对照表"""
        if not cls.is_score_valid(score):
            raise ValueError("成绩必须在0-100之间！")
        
        if score >= 90:
            return 4.0
        elif score >= 85:
            return 3.7
        elif score >= 80:
            return 3.3
        elif score >= 76:
            return 3.0
        elif score >= 73:
            return 2.7
        elif score >= 70:
            return 2.3
        elif score >= 66:
            return 2.0
        elif score >= 63:
            return 1.7
        elif score >= 61:
            return 1.3
        elif score == 60:
            return 1.0
        else:
            return cls.MIN_GPA

    @classmethod
    def calc_gpa_by_grade(cls, grade: str) -> float:
        """等级制成绩转绩点，支持十二级字母等级+五级中文等级"""
        if not grade or grade.isspace():
            return cls.MIN_GPA
        
        format_grade = grade.strip().upper()
        grade_map = {
            "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
            "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0,
            "优秀": 4.0, "良好": 3.3, "中等": 2.7, "及格": 2.0, "不及格": 0.0
        }
        
        if format_grade not in grade_map:
            valid_grades = ",".join(grade_map.keys())
            raise ValueError(f"无效的等级！支持的等级：{valid_grades}")
        
        return grade_map[format_grade]

    @classmethod
    def calc_weighted_gpa(cls, gpa: float, credit: int) -> float:
        """计算单门课程加权绩点"""
        if not cls.is_credit_valid(credit):
            raise ValueError("学分必须大于0！")
        return gpa * credit

    @classmethod
    def calc_total_gpa(cls, courses: List[Dict[str, Any]]) -> Dict[str, float]:
        """批量计算总学分、总加权绩点、平均加权绩点"""
        if not courses:
            raise ValueError("课程列表不能为空！")
        
        total_credit = 0
        total_weighted_gpa = 0.0

        for course in courses:
            # 校验必填字段
            if "credit" not in course:
                raise ValueError("每门课程必须包含credit（学分）字段")
            credit = int(course["credit"])
            if not cls.is_credit_valid(credit):
                raise ValueError(f"课程[{course.get('course_name', '未知')}]学分必须大于0")
            
            # 计算单门绩点
            if "score" in course:
                score = int(course["score"])
                gpa = cls.calc_gpa_by_score(score)
            elif "grade" in course:
                grade = course["grade"]
                gpa = cls.calc_gpa_by_grade(grade)
            else:
                raise ValueError(f"课程[{course.get('course_name', '未知')}]必须包含score（百分制）或grade（等级制）字段")
            
            # 累加计算
            total_credit += credit
            total_weighted_gpa += cls.calc_weighted_gpa(gpa, credit)
        
        # 计算平均绩点
        avg_gpa = total_weighted_gpa / total_credit if total_credit > 0 else 0.0

        return {
            "total_credit": total_credit,
            "total_weighted_gpa": round(total_weighted_gpa, 2),
            "avg_weighted_gpa": round(avg_gpa, 2)
        }

    @classmethod
    def is_score_valid(cls, score: int) -> bool:
        """校验百分制成绩合法性"""
        return isinstance(score, int) and 0 <= score <= 100

    @classmethod
    def is_credit_valid(cls, credit: int) -> bool:
        """校验学分合法性"""
        return isinstance(credit, int) and credit > 0

    @classmethod
    def get_scu_gpa_rule(cls) -> str:
        """获取四川大学官方绩点换算规则说明"""
        rule = """
        四川大学2017年秋季学期起执行十二级绩点换算标准：
        1. 百分制对应规则：
        - 100~90分：A，绩点4.0
        - 89~85分：A-，绩点3.7
        - 84~80分：B+，绩点3.3
        - 79~76分：B，绩点3.0
        - 75~73分：B-，绩点2.7
        - 72~70分：C+，绩点2.3
        - 69~66分：C，绩点2.0
        - 65~63分：C-，绩点1.7
        - 62~61分：D+，绩点1.3
        - 60分：D，绩点1.0
        - <60分：F，绩点0.0

        2. 等级制对应规则：
        - 优秀：4.0 | 良好：3.3 | 中等：2.7 | 及格：2.0 | 不及格：0.0
        """
        return rule.strip()

# ===================== 2. MCP服务器初始化 =====================
# 创建MCP服务器实例
scu_gpa_server = MCPServer(
    name="scu-gpa-server",
    description="四川大学本科生课程成绩与绩点核算服务，严格遵循川大官方十二级绩点标准，支持百分制/等级制换算、批量加权绩点计算"
)

# 实例化计算器
calculator = SCUGPACalculator()

# ===================== 3. 注册MCP工具（核心能力暴露） =====================
@scu_gpa_server.add_tool
def calc_single_course_gpa_by_score(course_name: str, credit: int, score: int) -> str:
    """
    计算单门课程绩点（百分制成绩）
    :param course_name: 课程名称，必填
    :param credit: 课程学分，必须大于0的整数，必填
    :param score: 课程百分制成绩，0-100之间的整数，必填
    :return: 课程绩点计算结果JSON字符串
    """
    try:
        gpa = calculator.calc_gpa_by_score(score)
        weighted_gpa = calculator.calc_weighted_gpa(gpa, credit)
        result = {
            "course_name": course_name,
            "credit": credit,
            "score": score,
            "single_gpa": round(gpa, 2),
            "weighted_gpa": round(weighted_gpa, 2),
            "status": "success"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False, indent=2)

@scu_gpa_server.add_tool
def calc_single_course_gpa_by_grade(course_name: str, credit: int, grade: str) -> str:
    """
    计算单门课程绩点（等级制成绩）
    :param course_name: 课程名称，必填
    :param credit: 课程学分，必须大于0的整数，必填
    :param grade: 课程等级，支持A/A-/B+/B/B-/C+/C/C-/D+/D/F、优秀/良好/中等/及格/不及格，必填
    :return: 课程绩点计算结果JSON字符串
    """
    try:
        gpa = calculator.calc_gpa_by_grade(grade)
        weighted_gpa = calculator.calc_weighted_gpa(gpa, credit)
        result = {
            "course_name": course_name,
            "credit": credit,
            "grade": grade,
            "single_gpa": round(gpa, 2),
            "weighted_gpa": round(weighted_gpa, 2),
            "status": "success"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False, indent=2)

@scu_gpa_server.add_tool
def calc_batch_courses_gpa(courses: str) -> str:
    """
    批量计算多门课程的总学分、总加权绩点、平均加权绩点
    :param courses: 课程列表JSON字符串，每门课程需包含course_name(可选)、credit(必填)、score/grade(二选一必填)
    :return: 批量绩点计算结果JSON字符串
    """
    try:
        course_list = json.loads(courses)
        calc_result = calculator.calc_total_gpa(course_list)
        result = {
            "course_count": len(course_list),
            **calc_result,
            "status": "success"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "课程列表必须是合法的JSON格式字符串"}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False, indent=2)

@scu_gpa_server.add_tool
def get_scu_gpa_standard_rule() -> str:
    """
    获取四川大学官方十二级绩点换算标准规则说明
    :return: 绩点规则说明文本
    """
    return calculator.get_scu_gpa_rule()

@scu_gpa_server.add_tool
def get_supported_grade_list() -> str:
    """
    获取支持的等级制成绩列表
    :return: 支持的等级列表JSON字符串
    """
    result = {
        "letter_grades": ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"],
        "chinese_grades": ["优秀", "良好", "中等", "及格", "不及格"],
        "status": "success"
    }
    return json.dumps(result, ensure_ascii=False, indent=2)

# ===================== 4. 服务器启动入口 =====================
if __name__ == "__main__":
    scu_gpa_server.run()