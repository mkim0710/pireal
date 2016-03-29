;NSIS Script Installer for Pireal

!define NAME "Pireal"
!define VERSION "1.0"
!define WEB_SITE "http://centaurialpha.github.io/pireal"
!define MUI_ABORTWARNING
!define MUI_LANGDLL_ALLLANGUAGES
!define MUI_ICON "icon.ico"

!include "MUI2.nsh"

Unicode true

SetCompressor lzma

Name "${NAME} ${VERSION}"
Caption "${NAME} for Windows"
OutFile "${NAME}-${VERSION}-setup.exe"

!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "sidebar.bmp"
!define MUI_LICENSEPAGE
!define MUI_COMPONENTSPAGE_NODESC

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "COPYING"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SpanishInternational"
!insertmacro MUI_RESERVEFILE_LANGDLL

CRCCheck on
; XPStyle on

InstallDir "$PROGRAMFILES\${NAME}"
InstallDirRegKey HKLM "Software\Pireal" ""
AutoCloseWindow false
ShowInstDetails show
SetOverwrite on
SetDataBlockOptimize on
SetCompress auto
UninstallText "Uninstall ${NAME}"

Section "pireal core"
  SectionIn RO
  SetOutPath "$INSTDIR"
  File /r "build\"
  SetShellVarContext all
  CreateDirectory "$SMPROGRAMS\${NAME}"
  CreateShortcut "$SMPROGRAMS\${NAME}\${NAME}.lnk" "$INSTDIR\${NAME}.exe"
  CreateShortcut "$DESKTOP\${NAME}.lnk" "$INSTDIR\${NAME}.exe"
  CreateShortcut "$SMPROGRAMS\${NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${NAME} "DisplayName" "${NAME} ${VERSION}"
  WriteRegStr HKLM SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${NAME} "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteUninstaller "Uninstall.exe"
  WriteRegStr HKLM SOFTWARE\${NAME} "InstallDir" $INSTDIR
  WriteRegStr HKLM SOFTWARE\${NAME} "Version" "${VERSION}"
  Exec "explorer $SMPROGRAMS\${NAME}\"
SectionEnd

Section /o "Samples"
  SetOutPath "$DOCUMENTS\${NAME}_samples"
  File /r "samples\"
  CreateDirectory "$DOCUMENTS\${NAME}_samples"
SectionEnd

Function .onInit
  SetOutPath $TEMP
  File /oname=spltmp.bmp "splash.bmp"
  splash::show 2300 $TEMP\spltmp
  Pop $0
  Delete $TEMP\spltmp.bmp
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Section "Uninstall"
  SetShellVarContext all
  RMDir /r "$SMPROGRAMS\${NAME}"
  RMDir /r "$INSTDIR\${NAME}"
  Delete "$DESKTOP\${NAME}.lnk"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM SOFTWARE\${NAME}
  DeleteRegKey HKLM Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}
SectionEnd