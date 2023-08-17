#include <memory>

template <class T>
std::shared_ptr<T> test_make_shared(T p) {
  return std::make_shared<T>(p);
}
template std::shared_ptr<int> test_make_shared(int);
template std::shared_ptr<long> test_make_shared(long);


