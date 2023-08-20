
#include <memory>
#include <utility>
#include <type_traits>
struct Base { explicit Base(int); Base() = default; Base(Base const&) = default; Base(Base&&) = default; };
struct Derived : Base {};


template <class T, class Y, class U = Y>
struct SharedPtrTests {
  using A = std::allocator<T>;
  using D = std::default_delete<T>;

  // constexpr shared_ptr() noexcept;
  static auto constexpr_shared_ptr_noexcept() {
    std::shared_ptr<T> result;
    return result;
  }
  
  // template<class Y> explicit shared_ptr(Y* p);
  static auto shared_ptr_constructor_with_Y_pointer(Y* p) {
    std::shared_ptr<T> result(p);
    return result;
  }
  
  // template<class Y, class D> shared_ptr(Y* p, D d);
  static auto shared_ptr_Y_D_overload(Y* p, D d) {
    std::shared_ptr<T> result(p, d);
    return result;
  }
  
  // template<class Y, class D, class A> shared_ptr(Y* p, D d, A a);
  static auto shared_ptr_with_Y_D_A(Y* p, D d, A a) {
    std::shared_ptr<T> result(p, d, a);
    return result;
  }
  
  // template <class D> shared_ptr(nullptr_t p, D d);
  static auto shared_ptr_nullptr_t_D_constructor(std::nullptr_t p, D d) {
    std::shared_ptr<T> result(p, d);
    return result;
  }
  
  // template <class D, class A> shared_ptr(nullptr_t p, D d, A a);
  static auto shared_ptr_declarative_nullptr_two_parameters(std::nullptr_t p, D d, A a) {
    std::shared_ptr<T> result(p, d, a);
    return result;
  }
  
  // template<class Y> shared_ptr(const shared_ptr<Y>& r, T *p) noexcept;
  static auto shared_ptr_const_shared_ptr_ref_T_ptr_noexcept(const std::shared_ptr<Y>& r, T* p) noexcept {
    std::shared_ptr<T> result(r, p);
    return result;
  }
  
  // shared_ptr(const shared_ptr& r) noexcept;
  static auto shared_ptr_copy_constructor(const std::shared_ptr<T>& r) {
    std::shared_ptr<T> result(r);
    return result;
  }
  
  // template<class Y> shared_ptr(const shared_ptr<Y>& r) noexcept;
  static auto shared_ptr_const_shared_ptr_Y_noexcept(const std::shared_ptr<Y>& r) noexcept {
    std::shared_ptr<T> result(r);
    return result;
  }
  
  // shared_ptr(shared_ptr&& r) noexcept;
  static auto shared_ptr_constructor_move_noexcept(std::shared_ptr<T>&& r) {
    std::shared_ptr<T> result(std::move(r));
    return result;
  }
  
  // template<class Y> shared_ptr(shared_ptr<Y>&& r) noexcept;
  static auto shared_ptr_move_constructor(std::shared_ptr<Y> &r) {
    std::shared_ptr<T> result(std::move(r));
    return result;
  }
  
  // template<class Y> explicit shared_ptr(const weak_ptr<Y>& r);
  static auto shared_ptr_weak_ptr_constructor(const std::weak_ptr<Y>& r) {
    std::shared_ptr<T> result(r);
    return result;
  }
  
  // template <class Y, class D> shared_ptr(unique_ptr<Y, D>&& r);
  static auto shared_ptr_with_unique_ptr(std::unique_ptr<Y, D>&& r) {
    std::shared_ptr<T> result(std::move(r));
    return result;
  }
  
  // shared_ptr(nullptr_t) : shared_ptr() { }
  static auto shared_ptr_constructor_nullptr() {
    std::shared_ptr<T> result(nullptr);
    return result;
  }
  
  // ~shared_ptr();
  static auto shared_ptr_destructor(std::shared_ptr<T> self) { 
    self.~shared_ptr();
  }
  
  // shared_ptr& operator=(const shared_ptr& r) noexcept;
  static auto shared_ptr_operator_assignment_copy(std::shared_ptr<T>& self, const std::shared_ptr<T>& r) {
    self = r;
    return self;
  }
  
  // template<class Y> shared_ptr& operator=(const shared_ptr<Y>& r) noexcept;
  static auto operator_assignment(std::shared_ptr<T>& self, const std::shared_ptr<Y>& r) {
      return self = r;
  }
  
  // shared_ptr& operator=(shared_ptr&& r) noexcept;
  static auto assign_move(std::shared_ptr<T>& self, std::shared_ptr<T>&& r) {
    return self.operator=(std::move(r)); 
  }
  
  // template<class Y> shared_ptr& operator=(shared_ptr<Y>&& r);
  static auto shared_ptr_operator_assignment_move(std::shared_ptr<T>& self, std::shared_ptr<Y>&& r) {
    return self = std::move(r);
  }

  // template <class Y, class D> shared_ptr& operator=(unique_ptr<Y, D>&& r);
  static auto operator_equals_unique_ptr(std::shared_ptr<T>& self, std::unique_ptr<Y, D>&& r) {
      return self = std::move(r);
  }
  
  // void swap(shared_ptr& r) noexcept;
  void swap_noexcept(std::shared_ptr<T>& self, std::shared_ptr<T>& r) {
    self.swap(r);
  }
  
  // void reset() noexcept;
  static auto reset_noexcept(std::shared_ptr<T>& self) {
    self.reset();
  }
  
  // template<class Y> void reset(Y* p);
  static auto reset_with_pointer(std::shared_ptr<T> self, Y* p) {
      return self.reset(p);
  }
  
  // template<class Y, class D> void reset(Y* p, D d);
  static auto reset_with_custom_deleter(std::shared_ptr<T> self, Y* p, D d) {
    self.reset(p, d);
  }
  
  // template<class Y, class D, class A> void reset(Y* p, D d, A a);
  static auto reset_with_deleter_and_allocator(std::shared_ptr<T> self, Y* p, D d, A a) { self.reset(p, d, a); }
  
  // T* get() const noexcept;
  static auto get_const_noexcept(const std::shared_ptr<T>& self) {
    return self.get();
  }
  
  // T& operator*() const noexcept;
  static auto operator_dereference_noexcept(std::shared_ptr<T> self) {
   T& result = *self;
    return result;
  }
  
  // T* operator->() const noexcept;
  static auto operator_arrow(const std::shared_ptr<T>& self) {
    return self.operator->();
  }
  
  // long use_count() const noexcept;
  static auto use_count(std::shared_ptr<T> self) {
    return self.use_count();
  }
  
  // bool unique() const noexcept;
  static auto unique_noargs(std::shared_ptr<T> self) {
    static auto result = self.unique();
    return result;
  }
  
  // explicit operator bool() const noexcept;
  static auto explicit_operator_bool(std::shared_ptr<T> self) {
      return static_cast<bool>(self);
  }
  
  // template<class U> bool owner_before(shared_ptr<U> const& b) const noexcept;
  static auto owner_before_shared_ptr(const std::shared_ptr<T> self, std::shared_ptr<U> const& b) noexcept {
   return self.owner_before(b);
  }
  
  // template<class U> bool owner_before(weak_ptr<U> const& b) const noexcept;
  bool owner_before_with_weak_ptr(const std::shared_ptr<T>& self, const std::weak_ptr<U>& b) noexcept {
    return self.owner_before(b);
  }

}; // end SharedPtrTests

template struct SharedPtrTests<Base, Derived>;
template struct SharedPtrTests<int, int, int>;
