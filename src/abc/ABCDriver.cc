#include <abc/Driver.h>

#include <stdio.h>
#include <string>

using namespace std;

Vlab::Theory::BigInteger getModelCount(string constraint, int bound) {
    Vlab::Driver driver;
    driver.InitializeLogger(0);
    driver.set_option(Vlab::Option::Name::REGEX_FLAG, 0x000f);
    std::istringstream str(constraint);
    driver.Parse(&str);
    driver.InitializeSolver();
    driver.Solve();
    Vlab::Theory::BigInteger count = driver.CountInts(bound);
    driver.reset();

    return count;
}

int main(void) {
    //checking if ABC works
    string cons = "(declare-fun x () Int)(assert (not (= x 0)))(check-sat)";
    getModelCount(cons,31);

    return 0;
}
