from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_template("请根据下面提标写一篇文章：{topic}")
value = prompt.invoke({"topic":"东北亚"})
print(value)
