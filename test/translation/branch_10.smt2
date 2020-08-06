(declare-const x10 Int)
(assert (and (>= x10 0) (x10 <= 4294967295)))
(assert (= x10 4294967200))
(declare-const x9 Int)
(assert (and (>= x9 (- 2147483648)) (<= x9 2147483647)))
(assert (= x9 x10 ) )

(check-sat)
