#!/usr/bin/perl

use strict;
use warnings;

sub Usage{
    print "usage: ParsingLog.pl <log file name>\n";
    exit;
}

my %SrcIpSessionCount;
my %DstPortSessionCount;

print Usage() if(!@ARGV);

my $filename = $ARGV[0];
open(my $fh, '<:encoding(UTF-8)', $filename)
  or die "Could not open file '$filename' $!";
 
while (my $row = <$fh>) {
  chomp $row;
  if ($row =~ /^[0-9]/) {
        $row =~ s/\s+/,/g;
  		#$row =~ s/\t/,/g;
  		my @rowArr = split (',', $row);
  		#print $rowArr[1].",".$rowArr[5]."\n";

  		if ($SrcIpSessionCount{$rowArr[1]}) {
                $SrcIpSessionCount{$rowArr[1]} = $SrcIpSessionCount{$rowArr[1]} + 1;
  		} else {
                $SrcIpSessionCount{$rowArr[1]} = 1;
  		}
        
        if ($DstPortSessionCount{$rowArr[5]}) {
                $DstPortSessionCount{$rowArr[5]} = $DstPortSessionCount{$rowArr[5]} + 1;
  		} else {
                $DstPortSessionCount{$rowArr[5]} = 1;
  		}
  }
  
}

my $outfilename_1 = $filename;
my $outfilename_2 = $filename;
   $outfilename_1 =~ s/.log/_SrcIpSessionCount.csv/;
   $outfilename_2 =~ s/.log/_DstPortSessionCount.csv/;
   

open(FH1, "> $outfilename_1") or die "Couldn't open $outfilename_1 for writing: $!";
	print FH1 "SrcIp,IpSessionCount\n";
	while (my ($SrcIp, $IpSessionCount) = each (%SrcIpSessionCount)) {  	
       print FH1 $SrcIp.",".$IpSessionCount."\n";
	}
close(FH1);
print $outfilename_1." done!\n";
   

open(FH2, "> $outfilename_2") or die "Couldn't open $outfilename_2 for writing: $!";
	print FH2 "DstPort,PortSessionCount\n";
	while (my ($DstPort, $PortSessionCount) = each (%DstPortSessionCount)) {  	
      	print FH2 $DstPort.",".$PortSessionCount."\n";
	}
close(FH2);
print $outfilename_2." done!\n";




