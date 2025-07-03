{
  outputs =
    { self }:
    {
      inherit self;
      dotSlashDot = toString ./.;
    };
}
