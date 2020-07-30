(declare-const x6 Int)
(assert (and (>= x6 (- 2147483648)) (<= x6 2147483647)))
(assert (= x6 (- 42)))
(declare-const x5 Int)
(assert (and (>= x5 (- 128)) (<= x5 127 )))
(assert (= x5 x6 ) )

(check-sat)
