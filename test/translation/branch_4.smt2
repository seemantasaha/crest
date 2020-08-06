(declare-const x4 Int)
(assert (and (>= x4 0) (<= x4 65535)))
(declare-const x3 Int)
(assert (and (>= x3 (- 2147483648)) (<= x3 2147483647)))
(assert (= x3 x4 ) )

(check-sat)
