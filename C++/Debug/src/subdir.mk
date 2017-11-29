################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
../src/VdASCIIFile.cpp \
../src/VdDataset.cpp \
../src/VdFile.cpp \
../src/VdObjFile.cpp \
../src/VdPoint.cpp \
../src/VdSQLite.cpp \
../src/VdTxtFile.cpp \
../src/VdXYZ.cpp \
../src/VdXYZFile.cpp \
../src/main.cpp 

O_SRCS += \
../src/velo.o 

OBJS += \
./src/VdASCIIFile.o \
./src/VdDataset.o \
./src/VdFile.o \
./src/VdObjFile.o \
./src/VdPoint.o \
./src/VdSQLite.o \
./src/VdTxtFile.o \
./src/VdXYZ.o \
./src/VdXYZFile.o \
./src/main.o 

CPP_DEPS += \
./src/VdASCIIFile.d \
./src/VdDataset.d \
./src/VdFile.d \
./src/VdObjFile.d \
./src/VdPoint.d \
./src/VdSQLite.d \
./src/VdTxtFile.d \
./src/VdXYZ.d \
./src/VdXYZFile.d \
./src/main.d 


# Each subdirectory must supply rules for building sources it contributes
src/%.o: ../src/%.cpp
	@echo 'Building file: $<'
	@echo 'Invoking: GCC C++ Compiler'
	g++ -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


