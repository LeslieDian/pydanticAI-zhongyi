// Neo4j 图谱 DDL (手册 §7).
CREATE CONSTRAINT symptom_name IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT syndrome_name IF NOT EXISTS FOR (s:Syndrome) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT treatment_name IF NOT EXISTS FOR (t:Treatment) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT formula_name IF NOT EXISTS FOR (f:Formula) REQUIRE f.name IS UNIQUE;
CREATE CONSTRAINT herb_name IF NOT EXISTS FOR (h:Herb) REQUIRE h.name IS UNIQUE;
CREATE CONSTRAINT case_id IF NOT EXISTS FOR (c:Case) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT text_ref IF NOT EXISTS FOR (t:Text) REQUIRE t.ref IS UNIQUE;

// 麻黄汤 示例
CREATE (s1:Symptom {name: "恶寒", category: "表", aliases: ["畏寒", "怕冷"]});
CREATE (s2:Symptom {name: "发热", category: "表"});
CREATE (s3:Symptom {name: "头痛", category: "表"});
CREATE (s4:Symptom {name: "无汗", category: "表"});
CREATE (s5:Symptom {name: "脉浮紧", category: "脉"});

CREATE (sy:Syndrome {name: "风寒表实证", definition: "风寒之邪侵袭表位"});
CREATE (t1:Treatment {name: "辛温解表", description: "以辛温之品发汗开迫"});
CREATE (f1:Formula {name: "麻黄汤", source: "伤寒论"});

CREATE (h1:Herb {name: "麻黄", nature: "微温", flavor: "辛", meridian: "肺", toxicity: "无毒"});
CREATE (h2:Herb {name: "桂枝", nature: "温", flavor: "甘辛", meridian: "心肺胃", toxicity: "无毒"});
CREATE (h3:Herb {name: "杏仁", nature: "微温", flavor: "苦", meridian: "肺大肠", toxicity: "无毒"});
CREATE (h4:Herb {name: "甘草", nature: "平", flavor: "甘", meridian: "多经", toxicity: "无毒"});

CREATE (f1)-[:CONTAINS {role: "君", dose_g: 9.0}]->(h1);
CREATE (f1)-[:CONTAINS {role: "臣", dose_g: 6.0}]->(h2);
CREATE (f1)-[:CONTAINS {role: "佐", dose_g: 9.0}]->(h3);
CREATE (f1)-[:CONTAINS {role: "使", dose_g: 3.0}]->(h4);

CREATE (s1)-[:INDICATES]->(sy);
CREATE (s2)-[:INDICATES]->(sy);
CREATE (s3)-[:INDICATES]->(sy);
CREATE (s4)-[:INDICATES]->(sy);
CREATE (s5)-[:INDICATES]->(sy);
CREATE (sy)-[:TREATED_BY]->(t1);
CREATE (t1)-[:USES]->(f1);
