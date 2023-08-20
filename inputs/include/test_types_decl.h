namespace test_types {

constexpr struct InitTagT {} InitTag{};

struct NonTrivial {
  NonTrivial();
  NonTrivial(InitTagT);
  NonTrivial(NonTrivial const&);
  NonTrivial& operator=(NonTrivial const&);
  ~NonTrivial();

  int buff[10];
};
struct Trivial {
  Trivial() = default;
  Trivial(InitTagT);

  int buff[10];
};

template <class Base = Trivial>
struct MoveOnly : Base {
  MoveOnly(MoveOnly const&) = delete;
  MoveOnly(MoveOnly&&) = default;
  MoveOnly() = default;
  MoveOnly& operator=(MoveOnly const&) = delete;
  MoveOnly& operator=(MoveOnly&&) = default;
};

template<typename T, class Base = Trivial>
class ForwardIterator {
public:
    // required members...
private:
  Trivial obj_;
};

template<typename T, class Base = Trivial>
class BidirectionalIterator {
public:
    // required members...
private:
    Base trivial;
};

template<typename T, class Base = Trivial>
class RandomAccessIterator {
public:
    // Required members...
private:
    Base obj_;  // pointer to the current element
};

} // namespace test_types
