template <typename T> struct S {
  T bar(T p) { return p; }
};
void foo() {
  struct S<int> s;
}
