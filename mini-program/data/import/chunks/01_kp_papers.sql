INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (1, '函数、极限与连续', 'limits-continuity', 'calculus', NULL, 0) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (2, '函数性质', 'function-properties', 'calculus', 1, 0) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (3, '数列极限', 'sequence-limit', 'calculus', 1, 1) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (4, '函数极限', 'function-limit', 'calculus', 1, 2) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (5, '无穷小与无穷大', 'infinitesimal-infinite', 'calculus', 1, 3) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (6, '连续与间断点', 'continuity-discontinuity', 'calculus', 1, 4) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (7, '一元函数微分学', 'single-variable-differential', 'calculus', NULL, 1) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (8, '导数与微分', 'derivative-differential', 'calculus', 7, 0) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (9, '中值定理', 'mean-value-theorem', 'calculus', 7, 1) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (10, 'Taylor公式', 'taylor-formula', 'calculus', 7, 2) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (11, '单调性与极值', 'monotonicity-extrema', 'calculus', 7, 3) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (12, '凹凸性与拐点', 'concavity-inflection', 'calculus', 7, 4) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (13, '渐近线', 'asymptote', 'calculus', 7, 5) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (14, '一元函数积分学', 'single-variable-integral', 'calculus', NULL, 2) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (15, '不定积分', 'indefinite-integral', 'calculus', 14, 0) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (16, '定积分', 'definite-integral', 'calculus', 14, 1) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (17, '定积分应用', 'definite-integral-application', 'calculus', 14, 2) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (18, '反常积分', 'improper-integral', 'calculus', 14, 3) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (19, '含参积分', 'parameter-integral', 'calculus', 14, 4) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (20, '多元函数微分学', 'multivariable-differential', 'calculus', NULL, 3) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (21, '多元函数极限与连续', 'multivariable-limit-continuity', 'calculus', 20, 0) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (22, '偏导数与全微分', 'partial-total-differential', 'calculus', 20, 1) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (23, '复合函数与隐函数', 'composite-implicit-function', 'calculus', 20, 2) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (24, '方向导数与梯度', 'directional-derivative-gradient', 'calculus', 20, 3) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (25, '多元函数极值', 'multivariable-extrema', 'calculus', 20, 4) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (26, 'Lagrange乘数法', 'lagrange-multiplier', 'calculus', 20, 5) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (27, '重积分', 'multiple-integral', 'calculus', NULL, 4) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (28, '二重积分', 'double-integral', 'calculus', 27, 0) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (29, '三重积分', 'triple-integral', 'calculus', 27, 1) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (30, '坐标变换', 'coordinate-transform', 'calculus', 27, 2) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (31, '曲线积分与曲面积分', 'line-surface-integral', 'calculus', NULL, 5) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (32, '第一、第二类曲线积分', 'line-integral', 'calculus', 31, 0) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (33, '第一、第二类曲面积分', 'surface-integral', 'calculus', 31, 1) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (34, 'Green公式', 'green-formula', 'calculus', 31, 2) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (35, 'Gauss公式', 'gauss-formula', 'calculus', 31, 3) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (36, 'Stokes公式', 'stokes-formula', 'calculus', 31, 4) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (37, '无穷级数', 'infinite-series', 'calculus', NULL, 6) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (38, '数项级数', 'number-series', 'calculus', 37, 0) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (39, '幂级数', 'power-series', 'calculus', 37, 1) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (40, 'Fourier级数', 'fourier-series', 'calculus', 37, 2) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (41, '常微分方程', 'ordinary-differential-equation', 'calculus', NULL, 7) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (42, '一阶微分方程', 'first-order-ode', 'calculus', 41, 0) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (43, '高阶微分方程', 'higher-order-ode', 'calculus', 41, 1) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (44, '微分方程综合应用', 'ode-application', 'calculus', 41, 2) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (45, '空间解析几何', 'spatial-analytic-geometry', 'calculus', NULL, 8) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (46, '向量与坐标', 'vector-coordinate', 'calculus', 45, 0) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (47, '空间平面与直线', 'plane-line', 'calculus', 45, 1) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (48, '曲面与曲线', 'surface-curve', 'calculus', 45, 2) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (49, '决赛·线性代数', 'final-linear-algebra', 'final_linear_algebra', NULL, 9) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (50, '行列式与矩阵', 'determinant-matrix', 'final_linear_algebra', 49, 0) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (51, '线性方程组', 'linear-equation-system', 'final_linear_algebra', 49, 1) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (52, '向量组', 'vector-group', 'final_linear_algebra', 49, 2) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (53, '特征值与特征向量', 'eigenvalue', 'final_linear_algebra', 49, 3) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) VALUES (54, '二次型', 'quadratic-form', 'final_linear_algebra', 49, 4) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (2, 1, 'final', '2010 年第一届全国大学生数学竞赛决赛（非数学专业）', '非数学专业', 2010, 'papers/edition-01/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (1, 1, 'preliminary', '2009 年第一届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2009, 'papers/edition-01/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (4, 2, 'final', '2011 年第二届全国大学生数学竞赛决赛（非数学专业）', '非数学专业', 2011, 'papers/edition-02/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (3, 2, 'preliminary', '2010 年第二届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2010, 'papers/edition-02/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (6, 3, 'final', '2012 年第三届全国大学生数学竞赛决赛（非数学专业）', '非数学专业', 2012, 'papers/edition-03/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (5, 3, 'preliminary', '2011 年第三届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2011, 'papers/edition-03/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (8, 4, 'final', '2013 年第四届全国大学生数学竞赛决赛（非数学类）', '非数学类', 2013, 'papers/edition-04/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (7, 4, 'preliminary', '2012 年第四届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2012, 'papers/edition-04/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (10, 5, 'final', '2014 年第五届全国大学生数学竞赛决赛（非数学类）', '非数学类', 2014, 'papers/edition-05/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (9, 5, 'preliminary', '2013 年第五届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2013, 'papers/edition-05/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (12, 6, 'final', '2015 年第六届全国大学生数学竞赛决赛（非数学类）', '非数学类', 2015, 'papers/edition-06/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (11, 6, 'preliminary', '2014 年第六届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2014, 'papers/edition-06/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (14, 7, 'final', '2016 年第七届全国大学生数学竞赛决赛（非数学专业）', '非数学专业', 2016, 'papers/edition-07/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (13, 7, 'preliminary', '2015 年第七届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2015, 'papers/edition-07/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (16, 8, 'final', '2017 年第八届全国大学生数学竞赛决赛（非数学类）', '非数学类', 2017, 'papers/edition-08/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (15, 8, 'preliminary', '2016 年第八届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2016, 'papers/edition-08/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (18, 9, 'final', '2018 年第九届全国大学生数学竞赛决赛（非数学专业）', '非数学专业', 2018, 'papers/edition-09/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (17, 9, 'preliminary', '2017 年第九届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2017, 'papers/edition-09/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (20, 10, 'final', '2019 年第十届全国大学生数学竞赛决赛（非数学专业）', '非数学专业', 2019, 'papers/edition-10/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (19, 10, 'preliminary', '2018 年第十届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2018, 'papers/edition-10/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (22, 11, 'final', '2021 年第十一届全国大学生数学竞赛决赛（非数学类）', '非数学类', 2021, 'papers/edition-11/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (21, 11, 'preliminary', '2019 年第十一届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2019, 'papers/edition-11/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (24, 12, 'final', '2021 年第十二届全国大学生数学竞赛决赛（非数学类）', '非数学类', 2021, 'papers/edition-12/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (23, 12, 'preliminary', '2020 年第十二届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2020, 'papers/edition-12/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (26, 13, 'final', '2023 年第十三届全国大学生数学竞赛决赛（非数学类）', '非数学类', 2023, 'papers/edition-13/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (25, 13, 'preliminary', '2021 年第十三届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2021, 'papers/edition-13/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (28, 14, 'final', '2023 年第十四届全国大学生数学竞赛决赛（非数学类）', '非数学类', 2023, 'papers/edition-14/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (27, 14, 'preliminary', '2022 年第十四届全国大学生数学竞赛初赛（非数学类）', '非数学类', 2022, 'papers/edition-14/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (30, 15, 'final', '2024 年第十五届全国大学生数学竞赛决赛（非数学类）', '非数学类', 2024, 'papers/edition-15/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (29, 15, 'preliminary', '2023 年第十五届全国大学生数学竞赛初赛（非数学A类）', '非数学A类', 2023, 'papers/edition-15/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (31, 15, 'preliminary_b', '2023 年第十五届全国大学生数学竞赛初赛（非数学B类）', '非数学B类', 2023, 'papers/edition-15/preliminary-b.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (33, 16, 'final', '2025 年第十六届全国大学生数学竞赛决赛（非数学A类）', '非数学A类', 2025, 'papers/edition-16/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (35, 16, 'final_b', '2025 年第十六届全国大学生数学竞赛决赛（非数学B类）', '非数学B类', 2025, 'papers/edition-16/final-b.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (32, 16, 'preliminary', '2024 年第十六届全国大学生数学竞赛初赛（非数学A类）', '非数学A类', 2024, 'papers/edition-16/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (34, 16, 'preliminary_b', '2024 年第十六届全国大学生数学竞赛初赛（非数学B类）', '非数学B类', 2024, 'papers/edition-16/preliminary-b.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (37, 17, 'final', '2026 年第十七届全国大学生数学竞赛决赛（非数学A类）', '非数学A类', 2026, 'papers/edition-17/final.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (39, 17, 'final_b', '2026 年第十七届全国大学生数学竞赛决赛（非数学B类）', '非数学B类', 2026, 'papers/edition-17/final-b.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (36, 17, 'preliminary', '2025 年第十七届全国大学生数学竞赛初赛（非数学A类）', '非数学A类', 2025, 'papers/edition-17/preliminary.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;

INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) VALUES (38, 17, 'preliminary_b', '2025 年第十七届全国大学生数学竞赛初赛（非数学B类）', '非数学B类', 2025, 'papers/edition-17/preliminary-b.pdf', 'published') ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;
