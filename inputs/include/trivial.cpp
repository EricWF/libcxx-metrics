#include "test_types.h"

namespace test_types {

Trivial::Trivial(InitTagT) : x(42) {
    // TODO: Write your code here
}

Trivial::Trivial(int x) noexcept  : x(x) {
    // TODO: Write your code here
}

bool operator==(const Trivial& lhs, const Trivial& rhs) noexcept {
    return lhs.x == rhs.x;
}

bool operator!=(const Trivial& lhs, const Trivial& rhs) noexcept {
    return !(lhs == rhs);
}

bool operator<(const Trivial& lhs, const Trivial& rhs) noexcept {
    return lhs.x < rhs.x;
}

} // namespace test_types
