VERSION="21.1.10.0"
OutFile="vcxsrv-64.${VERSION}.portable.tar"

rm -f $OutFile
rm -f $OutFile.gz

tar -cf $OutFile -C ../obj64/servrelease vcxsrv.exe
tar -rf $OutFile -C ../dix protocol.txt
tar -rf $OutFile -C .. system.XWinrc
tar -rf $OutFile -C .. X0.hosts
tar -rf $OutFile -C ../../../third_party/xorg/xkbcomp/obj64/release xkbcomp.exe
tar -rf $OutFile -C ../../../third_party/xorg/apps/xhost/obj64/release xhost.exe
tar -rf $OutFile -C ../../../third_party/xorg/apps/xrdb/obj64/release xrdb.exe
tar -rf $OutFile -C ../../../third_party/xorg/apps/xauth/obj64/release xauth.exe
tar -rf $OutFile -C ../../../third_party/xorg/apps/xcalc/obj64/release xcalc.exe
tar -rf $OutFile -C ../../../third_party/xorg/apps/xcalc/app-defaults xcalc
tar -rf $OutFile -C ../../../third_party/xorg/apps/xcalc/app-defaults xcalc-color
tar -rf $OutFile -C ../../../third_party/xorg/apps/xclock/obj64/release xclock.exe
tar -rf $OutFile -C ../../../third_party/xorg/apps/xclock/app-defaults xclock
tar -rf $OutFile -C ../../../third_party/xorg/apps/xclock/app-defaults xclock-color
tar -rf $OutFile -C ../../../third_party/xorg/apps/xwininfo/obj64/release xwininfo.exe
tar -rf $OutFile -C .. XKeysymDB
tar -rf $OutFile -C ../../../third_party/xorg libX11/src/XErrorDB
tar -rf $OutFile -C ../../../third_party/xorg libX11/src/xcms/Xcms.txt
tar -rf $OutFile -C .. XtErrorDB
tar -rf $OutFile -C .. font-dirs
tar -rf $OutFile -C .. .Xdefaults
tar -rf $OutFile -C ../hw/xwin/xlaunch/obj64/release xlaunch.exe
tar -rf $OutFile -C ../../../tools/plink/obj64/release plink.exe
tar -rf $OutFile -C ../../../third_party/graphics/mesalib/src/obj64/release swrast_dri.dll
tar -rf $OutFile -C ../hw/xwin/swrastwgl_dri/obj64/release swrastwgl_dri.dll
tar -rf $OutFile -C ../../../third_party/graphics/dxtn/obj64/release dxtn.dll
tar -rf $OutFile -C ../../../third_party/libxml2/build/x64/Release libxml2.dll
tar -rf $OutFile -C ../../../third_party/libiconv/build/x64/Release libiconv.dll
tar -rf $OutFile -C ../../../third_party/xorg/xkbcomp --transform='s|^|licenses/xkbcomp/|' COPYING README.vcxsrv.md
tar -rf $OutFile -C ../../../third_party/xorg/libXpm --transform='s|^|licenses/libXpm/|' COPYING COPYRIGHT README.vcxsrv.md
tar -rf $OutFile -C ../../../third_party/zlib --transform='s|^|licenses/zlib/|' LICENSE README.vcxsrv.md
tar -rf $OutFile -C ../../../third_party/openssl --transform='s|^LICENSE.txt$|licenses/openssl/LICENSE.txt|;s|^README.vcxsrv.md$|licenses/openssl/README.vcxsrv.md|' LICENSE.txt README.vcxsrv.md
tar -rf $OutFile -C ../../../third_party/expat --transform='s|^COPYING$|licenses/expat/COPYING|;s|^README.vcxsrv.md$|licenses/expat/README.vcxsrv.md|' COPYING README.vcxsrv.md
tar -rf $OutFile -C ../../../third_party/libxml2 --transform='s|^source/Copyright$|licenses/libxml2/Copyright|;s|^README.vcxsrv.md$|licenses/libxml2/README.vcxsrv.md|' source/Copyright README.vcxsrv.md
tar -rf $OutFile -C ../../../third_party/libiconv --transform='s|^source/|licenses/libiconv/|;s|^README.vcxsrv.md$|licenses/libiconv/README.vcxsrv.md|' source/COPYING.LIB source/COPYING README.vcxsrv.md
tar -rf $OutFile -C ../../../third_party/zlib/obj64/release zlib1.dll
tar -rf $OutFile -C ../../../third_party/xorg/libxcb/src/obj64/release libxcb.dll
tar -rf $OutFile -C ../../../third_party/xorg/libXau/obj64/release libXau.dll
tar -rf $OutFile -C ../../../third_party/xorg/libX11/obj64/release libX11.dll
tar -rf $OutFile -C ../../../third_party/xorg/libXext/src/obj64/release libXext.dll
tar -rf $OutFile -C ../../../third_party/xorg/libXmu/src/obj64/release libXmu.dll
tar -rf $OutFile -C ../../../third_party/openssl/release64 libcrypto-3-x64.dll
tar -rf $OutFile -C ../../../third_party/fonts/freetype/objs/x64/Release freetype.dll
tar -rf $OutFile vcruntime140.dll
tar -rf $OutFile vcruntime140_1.dll
tar -rf $OutFile msvcp140.dll
tar -rf $OutFile -C .. xkbdata
tar -rf $OutFile -C .. locale
tar -rf $OutFile -C .. bitmaps
tar -rf $OutFile -C .. fonts

gzip $OutFile
