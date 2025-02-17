class FreedValidator < Formula
  include Language::Python::Virtualenv

  desc "Toolkit for validating and testing FreeD protocol data streams"
  homepage "https://github.com/koensayr/freed_test"
  url "https://github.com/koensayr/freed_test/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "UPDATE_WITH_ACTUAL_SHA256_AFTER_RELEASE"
  license "MIT"

  depends_on "python@3.10"

  resource "colorama" do
    url "https://files.pythonhosted.org/packages/d8/53/6f443c9a4a8358a93a6792e2acffb9d9d5cb0a5cfd8802644b7b1c9a02e4/colorama-0.4.6.tar.gz"
    sha256 "08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44"
  end

  resource "pandas" do
    url "https://files.pythonhosted.org/packages/46/f8/b217a5762f8fe30b8b032bb5d31862e439467c8ef3cf9c0f24c4cbb9dd42/pandas-1.5.3.tar.gz"
    sha256 "bed7d865975a2d68be33481bd7e50144d6f472c9691c2c7e0a0dd612d2c5f35a"
  end

  resource "matplotlib" do
    url "https://files.pythonhosted.org/packages/ad/5a/19cc79a30f0b224610a85aef1e40ffb3c8f4462c08d2f365ecc652966b8e/matplotlib-3.7.2.tar.gz"
    sha256 "a8caf4a30d88a2bea514c73a7c6c4a14f029a7139559e1c16b94ee32b6fd7567"
  end

  resource "seaborn" do
    url "https://files.pythonhosted.org/packages/4c/2b/667a21141a46ad5aa2c12c75422c5eab33553b2775c6d2b46c5b0d1c01b7/seaborn-0.12.2.tar.gz"
    sha256 "374645f36509d0dcab895cba5b47daf0586f77bfe642501a640f2d4ba9e47772"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    # Test help commands
    assert_match "FreeD Protocol Validator Toolkit", shell_output("#{bin}/freed --help")
    assert_match "UDP packet validator", shell_output("#{bin}/freed validate --help")
    assert_match "Generate test patterns", shell_output("#{bin}/freed simulate --help")
    
    # Test version output
    assert_match version.to_s, shell_output("#{bin}/freed --version")
    
    # Start validator in background and test with simulator
    require "open3"
    
    # Run validator in background
    Open3.popen3("#{bin}/freed validate --port 6789") do |_, stdout, _, thread|
      # Wait for startup message
      sleep(1)
      
      # Run simulator briefly
      system "#{bin}/freed simulate circle --duration 1 --port 6789"
      
      # Check validator output
      assert_match "Received packet", stdout.read
    ensure
      Process.kill("TERM", thread.pid)
    end
  end
end
