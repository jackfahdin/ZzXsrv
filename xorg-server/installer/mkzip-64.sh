VERSION="21.1.16.1"
OutFile="zzxsrv-64.${VERSION}.portable.tar"

rm -f $OutFile
rm -f $OutFile.gz

tar -cf $OutFile -C ../obj64/servrelease ZzXsrv.exe
tar -rf $OutFile -C ../dix protocol.txt
tar -rf $OutFile -C .. system.XWinrc
tar -rf $OutFile -C .. X0.hosts
tar -rf $OutFile -C ../../xkbcomp/obj64/release xkbcomp.exe
tar -rf $OutFile -C .. XKeysymDB
tar -rf $OutFile -C ../.. libX11/src/XErrorDB
tar -rf $OutFile -C ../.. libX11/src/xcms/Xcms.txt
tar -rf $OutFile -C .. XtErrorDB
tar -rf $OutFile -C .. font-dirs
tar -rf $OutFile -C .. .Xdefaults
tar -rf $OutFile -C ../../libxml2/bin64 libxml2-2.dll
tar -rf $OutFile -C ../../libxml2/bin64 libgcc_s_sjlj-1.dll
tar -rf $OutFile -C ../../libxml2/bin64 libiconv-2.dll
tar -rf $OutFile -C ../../libxml2/bin64 libwinpthread-1.dll
tar -rf $OutFile -C ../../zlib/obj64/release zlib1.dll
tar -rf $OutFile -C ../../libxcb/src/obj64/release libxcb.dll
tar -rf $OutFile -C ../../libXau/obj64/release libXau.dll
tar -rf $OutFile -C ../../libX11/obj64/release libX11.dll
tar -rf $OutFile -C ../../openssl/release64 libcrypto-3-x64.dll
tar -rf $OutFile -C ../../freetype/objs/x64/Release freetype.dll
tar -rf $OutFile vcruntime140.dll
tar -rf $OutFile vcruntime140_1.dll
tar -rf $OutFile msvcp140.dll
tar -rf $OutFile -C .. xkbdata
tar -rf $OutFile -C .. locale
tar -rf $OutFile -C .. bitmaps
tar -rf $OutFile -C .. fonts

gzip $OutFile
