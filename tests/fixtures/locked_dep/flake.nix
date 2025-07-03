{
  inputs.dep.url = "$depsPath";
  outputs =
    { self, dep }:
    {
      inherit self;
      dotSlashDot = toString dep;
      notOutPath = dep.outPath;
    };
}
