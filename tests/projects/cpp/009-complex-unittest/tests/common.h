#ifndef __ZENMAKE_TEST_CPP_UNITTEST_TEST_COMMON_H__
#define __ZENMAKE_TEST_CPP_UNITTEST_TEST_COMMON_H__

#include <iostream>

/*
It's not necessary to use real testing framework like gtest, boost.test,
catch2, etc to check/test building and running of tests. So here is some
primitive emulation.
*/

template<typename T>
bool expectEq(const T& v1, const T& v2) {
    if (v1 != v2) {
        std::cout << v1 << " is not equal to " << v2 << std::endl;
        return false;
    }

    return true;
}

#endif
