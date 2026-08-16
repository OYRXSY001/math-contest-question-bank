INSERT INTO questions (id, paper_id, question_no, sort_order, question_type, score, stem_md, answer_md, solution_md, search_text, source_page, status) VALUES ('114', '18', '5', '5', 'comprehensive', '12', '定义 \(H(x)=\sum_{i=1}^nx_i^2-\sum_{i=1}^{n-1}x_ix_{i+1}\)。

1. 证明对任意非零 \(x\in\mathbb R^n\)，\(H(x)>0\)；
2. 在约束 \(x_n=1\) 下求最小值。', '1. \(H\) 正定。 2. 最小值为 \((n+1)/(2n)\)。', '1. 对应三对角实对称矩阵的各阶顺序主子式均为正，故正定。
2. 驻点方程给出 \(2x_1=x_2\)、\(2x_i=x_{i-1}+x_{i+1}\)，结合 \(x_n=1\) 得 \(x_i=i/n\)。代入即得 \((n+1)/(2n)\)。', '2018 年第九届全国大学生数学竞赛决赛（非数学专业） 定义 (H(x)= i=1 nx i 2- i=1 n-1 x ix i+1 )。 1. 证明对任意非零 (x R n )， (H(x)>0 )； 2. 在约束 (x n=1 ) 下求最小值。 1. (H ) 正定。 2. 最小值为 ((n+1)/(2n) )。 1. 对应三对角实对称矩阵的各阶顺序主子式均为正，故正定。 2. 驻点方程给出 (2x 1=x 2 )、 (2x i=x i-1 +x i+1 )，结合 (x n=1 ) 得 (x i=i/n )。代入即得 ((n+1)/(2n) )。', '2', 'published') ON CONFLICT (id) DO NOTHING;
INSERT INTO questions (id, paper_id, question_no, sort_order, question_type, score, stem_md, answer_md, solution_md, search_text, source_page, status) VALUES ('115', '18', '6', '6', 'proof', '12', '设 \(f\in C^1(D)\)，\(D:x^2+y^2\le a^2\)，边界上 \(f=a^2\)，且 \(\max_D(f_x^2+f_y^2)=a^2\)。证明
\[\iint_Df(x,y)\,dxdy\le\frac{4\pi a^4}{3}.\]', '所给积分估计成立。', '分别对 \(P=yf,Q=0\) 与 \(P=0,Q=xf\) 使用 Green 公式，相加后把积分分成边界项与梯度项。边界项为 \(\pi a^4\)，梯度项由 Cauchy 不等式和极坐标积分至多为 \(\pi a^4/3\)。', '2018 年第九届全国大学生数学竞赛决赛（非数学专业） 设 (f C 1(D) )， (D:x 2+y 2 a 2 )，边界上 (f=a 2 )，且 ( D(f x 2+f y 2)=a 2 )。证明 [ Df(x,y) ,dxdy 4 a 4 3 . ] 所给积分估计成立。 分别对 (P=yf,Q=0 ) 与 (P=0,Q=xf ) 使用 Green 公式，相加后把积分分成边界项与梯度项。边界项为 ( a 4 )，梯度项由 Cauchy 不等式和极坐标积分至多为 ( a 4/3 )。', '2', 'published') ON CONFLICT (id) DO NOTHING;
INSERT INTO questions (id, paper_id, question_no, sort_order, question_type, score, stem_md, answer_md, solution_md, search_text, source_page, status) VALUES ('116', '18', '7', '7', 'comprehensive', '12', '设 \(0<a_n<1\)，且 \(\displaystyle\frac{\ln(1/a_n)}{\ln n}\to q\)（有限或 \(+\infty\)）。

1. 证明 \(q>1\) 时 \(\sum a_n\) 收敛，\(q<1\) 时发散；
2. 讨论 \(q=1\) 时的敛散性。', '1. 结论如题。 2. \(q=1\) 时可能收敛，也可能发散。', '当 \(q>1\) 时选 \(1<p<q\)，充分大时 \(a_n<n^{-p}\)；当 \(q<1\) 时选 \(q<p<1\)，充分大时 \(a_n>n^{-p}\)。当 \(q=1\) 时，\(a_n=1/n\) 给出发散例，\(a_n=1/[n(\ln n)^2]\) 给出收敛例。', '2018 年第九届全国大学生数学竞赛决赛（非数学专业） 设 (0<a n<1 )，且 ( (1/a n) n q )（有限或 (+ )）。 1. 证明 (q>1 ) 时 ( a n ) 收敛， (q<1 ) 时发散； 2. 讨论 (q=1 ) 时的敛散性。 1. 结论如题。 2. (q=1 ) 时可能收敛，也可能发散。 当 (q>1 ) 时选 (1<p<q )，充分大时 (a n<n -p )；当 (q<1 ) 时选 (q<p<1 )，充分大时 (a n>n -p )。当 (q=1 ) 时， (a n=1/n ) 给出发散例， (a n=1/[n( n) 2] ) 给出收敛例。', '2', 'published') ON CONFLICT (id) DO NOTHING;
INSERT INTO questions (id, paper_id, question_no, sort_order, question_type, score, stem_md, answer_md, solution_md, search_text, source_page, status) VALUES ('117', '19', '1', '1', 'calculation', '24', '填空题，共 4 小题，每小题 6 分。

1. 设 \(0<\alpha<1\)，求 \(\displaystyle\lim_{n\to\infty}[(n+1)^\alpha-n^\alpha]\)。
2. 曲线由 \(x=t+\cos t\)、\(e^y+ty+\sin t=1\) 确定，求 \(t=0\) 对应点处的切线。
3. 求 \(\displaystyle\int\frac{\ln(x+\sqrt{1+x^2})}{(1+x^2)^{3/2}}\,dx\)。
4. 求 \(\displaystyle\lim_{x\to0}\frac{1-\cos x\,(\cos2x)^{1/2}(\cos3x)^{1/3}}{x^2}\)。', '1. \(0\)。 2. \(y=-x+1\)。
3. \(\displaystyle\frac{x}{\sqrt{1+x^2}}\ln(x+\sqrt{1+x^2})-\frac12\ln(1+x^2)+C\)。
4. \(3\)。', '1. 用凹函数估计或令 \(x=1/n\) 化为等价无穷小。
2. 对参数方程求导，代入 \(t=0,x=1,y=0\)，得斜率 \(-1\)。
3. 令 \(x=\tan t\) 并分部积分。
4. 对三个余弦因子作二阶 Taylor 展开，乘积为 \(1-3x^2+o(x^2)\)。', '2018 年第十届全国大学生数学竞赛初赛（非数学类） 填空题，共 4 小题，每小题 6 分。 1. 设 (0< <1 )，求 ( n [(n+1) -n ] )。 2. 曲线由 (x=t+ t )、 (e y+ty+ t=1 ) 确定，求 (t=0 ) 对应点处的切线。 3. 求 ( (x+ 1+x 2 ) (1+x 2) 3/2 ,dx )。 4. 求 ( x 0 1- x ,( 2x) 1/2 ( 3x) 1/3 x 2 )。 1. (0 )。 2. (y=-x+1 )。 3. ( x 1+x 2 (x+ 1+x 2 )- 12 (1+x 2)+C )。 4. (3 )。 1. 用凹函数估计或令 (x=1/n ) 化为等价无穷小。 2. 对参数方程求导，代入 (t=0,x=1,y=0 )，得斜率 (-1 )。 3. 令 (x= t ) 并分部积分。 4. 对三个余弦因子作二阶 Taylor 展开，乘积为 (1-3x 2+o(x 2) )。', '1', 'published') ON CONFLICT (id) DO NOTHING;
INSERT INTO questions (id, paper_id, question_no, sort_order, question_type, score, stem_md, answer_md, solution_md, search_text, source_page, status) VALUES ('118', '19', '2', '2', 'calculation', '8', '设 \(f(t)\) 在 \(t\ne0\) 时一阶连续可导，且 \(f(1)=0\)。求 \(f(x^2-y^2)\)，使
\[\int_Ly[2-f(x^2-y^2)]\,dx+xf(x^2-y^2)\,dy\]
与路径无关，其中 \(L\) 为任一不与直线 \(y=\pm x\) 相交的分段光滑曲线。', '\(\displaystyle f(x^2-y^2)=1-\frac1{x^2-y^2}\)。', '由 \(P_y=Q_x\) 得 \(uf''(u)+f(u)-1=0\)，其通解为 \(f(u)=1+C/u\)。再由 \(f(1)=0\) 得 \(C=-1\)。', '2018 年第十届全国大学生数学竞赛初赛（非数学类） 设 (f(t) ) 在 (t 0 ) 时一阶连续可导，且 (f(1)=0 )。求 (f(x 2-y 2) )，使 [ Ly[2-f(x 2-y 2)] ,dx+xf(x 2-y 2) ,dy ] 与路径无关，其中 (L ) 为任一不与直线 (y= x ) 相交的分段光滑曲线。 ( f(x 2-y 2)=1- 1 x 2-y 2 )。 由 (P y=Q x ) 得 (uf''(u)+f(u)-1=0 )，其通解为 (f(u)=1+C/u )。再由 (f(1)=0 ) 得 (C=-1 )。', '1', 'published') ON CONFLICT (id) DO NOTHING;