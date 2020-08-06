(declare-const x2 Int)
(assert (and (>= x2 0) (<= x2 4294967295)))
(assert (= x2 4294967295))
(declare-const x1 Int)
(assert (and (>= x1 (- 2147483648)) (<= x1 2147483647)))
(assert (= x1 x2 ) )

(check-sat)

