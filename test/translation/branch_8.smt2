(declare-const x8 Int)
(assert (and (>= x8 (- 2147483648)) (<= x8 2147483647)))
(assert (= x8 (- 37)))
(declare-const x7 Int)
(assert (and (>= x7 0) (<= x7 65535)))
(assert (= x7 x8 ) )

(check-sat)
